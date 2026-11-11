"""Backfill SEC filing provenance in an existing Chroma collection without model calls."""

import argparse
import hashlib
import json
import shutil
import sqlite3
from collections import defaultdict
from datetime import date
from pathlib import Path

import chromadb

from config import config
from ingest import fetch_submissions, filing_document_url, get_cik

COLLECTION = "mda_filings"


def snapshot(collection):
    rows = collection.get(include=["metadatas", "documents", "embeddings"])
    return {key: rows[key] for key in ("ids", "metadatas", "documents", "embeddings")}


def digest_rows(rows):
    result = {}
    for index, record_id in enumerate(rows["ids"]):
        embedding = rows["embeddings"][index]
        result[record_id] = (
            rows["documents"][index],
            hashlib.sha256(embedding.tobytes()).hexdigest(),
        )
    return result


def plan(rows):
    groups = defaultdict(list)
    for index, meta in enumerate(rows["metadatas"]):
        groups[(meta["ticker"], meta["accession_number"])].append(index)

    submissions = {}
    changes = {}
    unresolved = []
    for (ticker, accession), indexes in sorted(groups.items()):
        if ticker not in submissions:
            cik = get_cik(ticker)
            payload = fetch_submissions(cik)
            recent = payload["filings"]["recent"]
            submissions[ticker] = (cik, {
                number: {key: recent[key][i] for key in ("form", "reportDate", "primaryDocument", "filingDate")}
                for i, number in enumerate(recent["accessionNumber"])
            })
        cik, filings = submissions[ticker]
        filing = filings.get(accession)
        if not filing or filing["form"] not in ("10-K", "10-Q") or not filing["reportDate"] or not filing["primaryDocument"]:
            unresolved.append({"ticker": ticker, "accession": accession, "chunks": len(indexes), "reason": "SEC submissions metadata unavailable"})
            continue
        period = date.fromisoformat(filing["reportDate"]).isoformat()
        url = filing_document_url(cik, accession, filing["primaryDocument"])
        for index in indexes:
            meta = rows["metadatas"][index]
            if meta.get("filing_date") != filing["filingDate"] or meta.get("form") != filing["form"]:
                unresolved.append({"ticker": ticker, "accession": accession, "chunks": len(indexes), "reason": "indexed filing identity disagrees with SEC"})
                break
            if any(meta.get(key) not in (None, value) for key, value in (("report_period_end", period), ("filing_url", url))):
                unresolved.append({"ticker": ticker, "accession": accession, "chunks": len(indexes), "reason": "existing metadata conflicts with SEC"})
                break
        else:
            for index in indexes:
                meta = rows["metadatas"][index]
                if meta.get("report_period_end") != period or meta.get("filing_url") != url:
                    changes[rows["ids"][index]] = {**meta, "report_period_end": period, "filing_url": url}
    return changes, unresolved, len(groups)


def backup_database(path, destination, rows):
    if destination.exists():
        raise FileExistsError(destination)
    destination.mkdir(parents=True)
    try:
        source = sqlite3.connect(f"file:{(path / 'chroma.sqlite3').resolve().as_posix()}?mode=ro", uri=True)
        target = sqlite3.connect(destination / "chroma.sqlite3")
        try:
            source.backup(target)
        finally:
            target.close()
            source.close()
        for item in path.iterdir():
            if item.is_dir():
                shutil.copytree(item, destination / item.name)
        backup_collection = chromadb.PersistentClient(path=str(destination)).get_collection(COLLECTION)
        copied = snapshot(backup_collection)
        if digest_rows(rows) != digest_rows(copied) or rows["metadatas"] != copied["metadatas"] or rows["ids"] != copied["ids"]:
            raise RuntimeError("Backup differs from original index")
    except Exception:
        raise RuntimeError(f"Backup validation failed; inspect {destination} before retrying") from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Back up and apply metadata updates")
    parser.add_argument("--backup", type=Path, help="New backup directory, required with --write")
    args = parser.parse_args()
    if args.write != (args.backup is not None):
        parser.error("--write requires --backup; --backup requires --write")
    db = Path(config.db_path).resolve()
    collection = chromadb.PersistentClient(path=str(db)).get_collection(COLLECTION)
    before = snapshot(collection)
    changes, unresolved, filings = plan(before)
    print(json.dumps({"chunks": len(before["ids"]), "filings": filings, "updates": len(changes), "unresolved": unresolved}, indent=2))
    if not args.write:
        return
    backup_database(db, args.backup.resolve(), before)
    ids = list(changes)
    for start in range(0, len(ids), 100):
        batch = ids[start:start + 100]
        collection.update(ids=batch, metadatas=[changes[id_] for id_ in batch])
    after = snapshot(collection)
    expected = {id_: metadata for id_, metadata in zip(before["ids"], before["metadatas"], strict=True)}
    expected.update(changes)
    actual = dict(zip(after["ids"], after["metadatas"], strict=True))
    if digest_rows(before) != digest_rows(after) or expected != actual:
        raise RuntimeError("Post-migration verification failed; retain backup")
    print(json.dumps({"verified_updates": len(changes), "backup": str(args.backup.resolve())}))


if __name__ == "__main__":
    main()

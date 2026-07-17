import re
from collections.abc import Sequence

_NUMBER_PATTERN = re.compile(
    r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(billion|million|thousand)?'
    r'|(\d+(?:\.\d+)?)%'
)

_METRIC_TRIGGERS = {
    "revenue", "sales", "cost", "expense", "income", "margin",
    "marketing", "labor", "food", "occupancy", "operating",
    "comparable", "same-restaurant", "digital", "diluted",
    "interest", "depreciation", "amortization", "impairment",
    "general", "administrative", "pre-opening", "restaurant",
}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$%.',-]+", text.lower())


def _find_numbers(text: str) -> list[dict]:
    results = []
    for m in _NUMBER_PATTERN.finditer(text):
        raw = m.group(0)
        if m.group(3):
            num = float(m.group(3))
            label = f"{num}%"
        else:
            num = float(m.group(1).replace(",", ""))
            unit = m.group(2) or ""
            label = f"${m.group(1)}{' ' + unit if unit else ''}"
        results.append({
            "raw": raw,
            "label": label,
            "value": num,
            "is_percent": bool(m.group(3)),
            "start": m.start(),
            "end": m.end(),
        })
    return results


def _first_occurrence(num_label: str, source_text: str) -> int | None:
    idx = source_text.lower().find(num_label.lower())
    if idx != -1:
        return idx
    normalized = num_label.lower().replace(" ", "")
    idx = source_text.lower().find(normalized)
    return idx if idx != -1 else None


def verify_answer(answer: str, sources: Sequence[dict | str]) -> dict:
    issues = []
    numbers = _find_numbers(answer)
    source_texts = [
        s["text"] if isinstance(s, dict) else s
        for s in sources
    ]
    all_source = " ".join(source_texts)
    answer_lower = answer.lower()

    for n in numbers:
        found = _first_occurrence(n["raw"], all_source)
        if found is None:
            window_start = max(0, n["start"] - 60)
            window_end = min(len(answer), n["end"] + 60)
            context = answer[window_start:window_end]
            metric_words = [
                w for w in _tokenize(context)
                if w in _METRIC_TRIGGERS
            ]
            issues.append({
                "type": "hallucinated_number",
                "value": n["raw"],
                "context": context.strip(),
                "metric_hint": metric_words[:3],
            })

    check_phrases = [
        (r"increased from \$?(\d+(?:\.\d+)?)", r"to \$?(\d+(?:\.\d+)?)"),
    ]
    for start_pat, end_pat in check_phrases:
        for m in re.finditer(start_pat, answer_lower):
            start_val = float(m.group(1))
            rest = answer_lower[m.end():]
            em = re.search(end_pat, rest)
            if em:
                end_val = float(em.group(1))
                if start_val < end_val:
                    continue
                window = answer[max(0, m.start() - 30):m.end() + em.end() + 30]
                if any(
                    _first_occurrence(f"{start_val}", t) and _first_occurrence(f"{end_val}", t)
                    for t in source_texts
                ):
                    issues.append({
                        "type": "inverted_direction",
                        "value": f"decreased {start_val} -> {end_val} but claims 'increased'",
                        "context": window.strip(),
                    })

    return {
        "answer": answer,
        "issues": issues,
        "has_issues": len(issues) > 0,
    }


class MetricVerifier:
    def __init__(self, synonym_groups: dict[str, list[str]] = None):
        from query_expansion import FINANCIAL_SYNONYMS
        self.synonym_groups = synonym_groups or FINANCIAL_SYNONYMS
        self._term_to_group = {}
        for group_name, terms in self.synonym_groups.items():
            for term in terms:
                self._term_to_group[term.lower()] = group_name

    def extract_metrics(self, text: str) -> list[str]:
        found = []
        for trigger in _METRIC_TRIGGERS:
            if trigger.lower() in text.lower():
                found.append(trigger)
        return found

    def resolve_group(self, metric_name: str) -> str | None:
        return self._term_to_group.get(metric_name.lower())

    def verify(self, answer: str, source_chunks: list[dict]) -> list[dict]:
        answer_metrics = self.extract_metrics(answer)
        source_metrics = set()
        for chunk in source_chunks:
            source_metrics.update(self.extract_metrics(chunk.get("text", "")))

        answer_groups = set()
        for m in answer_metrics:
            g = self.resolve_group(m)
            if g:
                answer_groups.add(g)

        source_groups = set()
        for m in source_metrics:
            g = self.resolve_group(m)
            if g:
                source_groups.add(g)

        mismatches = []
        for m in answer_metrics:
            g = self.resolve_group(m)
            if g and g not in source_groups:
                mismatches.append({
                    "metric": m,
                    "group": g,
                    "source_metrics": list(source_metrics),
                })

        return mismatches


def tag_chunk(chunk_text: str, base_metadata: dict) -> dict:
    from query_expansion import FINANCIAL_SYNONYMS

    text_lower = chunk_text.lower()
    metric_scores = {}
    for group_name, keywords in FINANCIAL_SYNONYMS.items():
        score = sum(1 for kw in keywords if kw.lower() in text_lower)
        if score >= 2:
            metric_scores[group_name] = score

    sorted_metrics = sorted(metric_scores.items(), key=lambda x: -x[1])
    enriched = dict(base_metadata)
    if sorted_metrics:
        enriched["metric"] = sorted_metrics[0][0]
        enriched["metric_keywords"] = ",".join(FINANCIAL_SYNONYMS[sorted_metrics[0][0]])
        enriched["metric_confidence"] = sorted_metrics[0][1]
    else:
        enriched["metric"] = "general"
        enriched["metric_keywords"] = ""
        enriched["metric_confidence"] = 0

    return enriched

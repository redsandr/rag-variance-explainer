"""Debug NLI model — test AutoModelForSequenceClassification fix."""
from nli import NLIClient

nli = NLIClient(threshold=0.72)

tests = [
    ("Revenue increased 7.4%.", "Revenue increased 7.4% to $3.1 billion driven by menu price increases.", "entailment"),
    ("Revenue was $3.1 billion.", "Revenue increased 7.4% to $3.1 billion driven by menu price increases.", "entailment"),
    ("Growth was driven by menu price increases.", "Revenue increased 7.4% to $3.1 billion driven by menu price increases.", "entailment"),
    ("Revenue decreased 5%.", "Revenue increased 7.4% to $3.1 billion.", "contradiction"),
    ("The company hired a new CEO.", "Revenue increased 7.4% to $3.1 billion.", "neutral"),
]

all_ok = True
for claim, chunk, expected in tests:
    result = nli.verify(claim, [chunk])
    ok = result["verdict"] == expected
    if not ok:
        all_ok = False
    status = "OK" if ok else "FAIL"
    print(f"{status} [{result['verdict']:>14}] entail={result['max_entailment']:.3f}  supported={result['supported']}  {claim}")

print(f"\n{'ALL TESTS PASSED' if all_ok else 'SOME TESTS FAILED'}")

nli.unload()

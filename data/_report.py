import json, os

d = json.load(open(os.path.join(os.path.dirname(__file__), 'faithfulness_results.json')))

print('=== Faithfulness Results ===')
print('Total claims:', d['total_claims'])
print('Overall strict:  {:.2f}%'.format(d['overall_faithfulness_strict']))
print('Overall weighted: {:.2f}%'.format(d['overall_faithfulness_weighted']))
print('Faithful:', d['faithful'])
print('Partial:', d['partial'])
print('Unfaithful:', d['unfaithful'])
print('Retrieval gaps:', d['retrieval_gaps'])

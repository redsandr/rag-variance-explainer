# Working on RAG Variance Explainer

At the start of every task, and again after context compaction, load the installed `poteto-mode` skill and apply the relevant playbook. If it is unavailable, use [the repository hardening skill](.agents/skills/rag-hardening/SKILL.md). Treat these as the first task constraints.

Read `git status` and the relevant diff before editing. Keep user changes intact, make coherent changes, and verify the actual behavior affected. Review new comments for purpose and remove narration. Report evidence and open risks.

For financial answers, a matching quote proves that text occurs in a retrieved passage. It does not prove a causal claim or arithmetic. Fail closed when structured parsing or quote validation fails. Keep execution of generated code out of the application process. See [the hardening skill](.agents/skills/rag-hardening/SKILL.md) for the full answer contract and release gates.

Use [the README](readme.md) for current setup and [GitHub readiness](docs/14.%20GitHub%20Readiness.md) for verified gates. Older numbered documents record experiments and historical results; recheck them against code before treating a claim as current.

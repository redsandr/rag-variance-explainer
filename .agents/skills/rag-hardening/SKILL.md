---
name: rag-hardening
description: Audit and improve RAG Variance Explainer for reliable financial answers, reproducible evaluation, clean code, and a standalone agent skill package. Use for work on this repository's pipeline, retrieval, verification, setup, docs, or Agensi readiness.
---

# RAG hardening

Read the installed `poteto-mode` skill at the start of each task and after a context summary. Apply its relevant playbook and principles. Use the available Codex tools when a T3-specific tool named by pstack is unavailable. User instructions and repository facts take precedence over the port's tool names.

## Work from evidence

1. Read Git status and the current diff before editing. Existing edits are part of the starting state. Keep each change reviewable.
2. State the behavior to prove, then inspect the actual code path. For bugs, reproduce the failure and fix the first incorrect decision.
3. Make one coherent change at a time. Check the result on the real code path before expanding scope.
4. Run `deslop` on changed code. Remove redundant branches, deep nesting, one-caller wrappers, abnormal defensive checks, and comments that only narrate code. Keep comments that explain a non-obvious constraint.
5. Apply `no-comments` to the final diff before review. Judge comments by whether the code or a check can express the constraint. Do not delete useful security or domain context just to reduce comment count.
6. Report what was verified, what remains uncertain, and the practical effect for a user and maintainer.

## Financial answer contract

- A retrieved quote matching source text proves only that the quote exists. It does not prove the answer's causal claim or arithmetic.
- Do not return model prose as a sourced answer when structured parsing, source reference, or quote validation fails. Abstain with an explicit reason.
- Treat NLI and LLM judging as fallible signals. Compare them with human-labeled cases before making accuracy claims.
- Do not execute LLM-generated Python inside the app process. AST checks and thread timeouts are not isolation boundaries. Keep PoT disabled until a supported isolated runner enforces time, CPU, memory, filesystem, and network limits.
- Keep evaluation numbers tied to a dataset version, model, configuration, command, and raw per-question results. Distinguish retrieval recall from answer faithfulness.

## Agensi gate

Package a skill only after a clean setup reproduces the documented workflow. The package must explain prerequisites, agent tools, first successful run, limits, license, and expected errors. Test it without assuming this repository or its MCP server is already installed. Prepare local artifacts; publish only when the user asks.

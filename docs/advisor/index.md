# AI Advisor

The fdars AI Advisor is a grounded analysis advisor that interprets computed
fdars diagnostics and recommends concrete parameter or method changes. It
operates across three surfaces — Python API, MCP server, and Agent Skill — all
sharing the same offline diagnostics core.

## Grounding Invariant

fdars computes every number. The LLM only interprets and cites those values.

![Grounding invariant: fdars computes numbers, the LLM only cites them](../assets/diagrams/advisor-grounding-invariant.svg){ .fdars-diagram }

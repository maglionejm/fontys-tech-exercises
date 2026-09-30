# The harness effect: same model, different results

Changing the harness while holding the model fixed changes benchmark scores by amounts that rival the differences between models. On SWE-bench Pro, Claude Opus 4.5 scored 45.9 percent under the standardized SEAL scaffold and 55.4 percent under Claude Code, a 9.5 point gap for the identical model; three harnesses on the same model spanned 50.2 to 55.4 percent. Third-party monitoring reported up to 11 points of scaffold-only variation for GPT-5 and 15 points for Kimi K2 Thinking on SWE-bench Verified. On Terminal-Bench 2, changing only the harness raised pass@1 from 69.7 to 77.0 percent.

The lesson for benchmark readers is to ask which harness produced a number. The lesson for builders is that the loop, the tools, the context rules and the verification steps are worth engineering: the model is the engine, but the harness decides how much of its power reaches the road.

Sources: "Stop Comparing LLM Agents Without Disclosing the Harness", arXiv 2605.23950, May 2026. "Harness or Model? Isolating the Harness Effect in Agentic Coding with a Contamination-Controlled Private Suite", arXiv 2609.11987, September 2026.

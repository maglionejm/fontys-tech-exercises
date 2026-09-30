---
name: cite-sources
description: Answer factual questions from the course library with a [source: id] citation, verified with check_citation before replying.
---
Use this skill whenever a question asks for a fact, a date or a number.

1. Search the library with search_docs using two to six key terms, never the whole question.
2. Read the best match with read_doc. If it does not answer the question, read the runner-up.
3. Draft an answer in one or two sentences taken from the document, and end it with the tag
   [source: <doc id>].
4. Call check_citation with the full draft. If it returns PROBLEM, fix the draft or read another
   document; never reply with an unverified claim.
5. Reply with the verified answer. If nothing in the library supports an answer, say so.

See checklist.md for the review checklist teachers apply to cited answers.

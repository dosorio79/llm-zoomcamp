# Homework 1 - Answers

## Q1. How many lesson pages?

* [ ] 24
* [x] 72
* [ ] 240
* [ ] 720

**Answer:**

---

## Q2. Indexing and searching

Query:

> How does the agentic loop keep calling the model until it stops?

What's the filename of the first result?

* [ ] `01-agentic-rag/lessons/03-rag.md`
* [x] `01-agentic-rag/lessons/14-agentic-loop.md`
* [ ] `04-evaluation/lessons/13-llm-as-judge.md`
* [ ] `06-best-practices/lessons/02-hybrid-search.md`

**Answer:**

---

## Q3. RAG

Query:

> How does the agentic loop keep calling the model until it stops?

How many input (prompt) tokens were sent to the model?

* [ ] 700
* [x] 7000
* [ ] 70000
* [ ] 700000

**Answer:**

---

## Q4. Chunking

Using:

```python
chunks = chunk_documents(
    documents,
    size=2000,
    step=1000
)
```

How many chunks do you get?

* [ ] 70
* [x] 295
* [ ] 1100
* [ ] 4500

**Answer:**

---

## Q5. RAG with chunking

Compared with Q3, how many fewer input tokens does the chunked version send?

* [ ] about the same
* [x] 3× fewer
* [ ] 10× fewer
* [ ] 30× fewer

**Answer:**

---

## Q6. Turning it into an agent

Question:

> How does the agentic loop work, and how is it different from plain RAG?

Using the instructions:

> You're a course teaching assistant. Answer the student's question using the search tool. Make multiple searches with different keywords before answering.

How many times did the agent call `search`?

* [ ] 0
* [ ] 4
* [ ] 10
* [ ] 20

**Answer:**

# Homework: Module 5 — Monitoring

## Q1. First trace

After instrumenting the `rag()`, `search()`, and `llm()` methods with OpenTelemetry spans, how many spans does one RAG trace produce?

* [ ] 1
* [x] 3
* [ ] 5
* [ ] 7

### Notes

The trace contains three spans:

* `rag`
* `search`
* `llm`

The `rag` span is the root span, while `search` and `llm` are child spans.

---

## Q2. Capturing metrics as span attributes

After recording the input and output token usage as attributes on the `llm` span, how many input tokens were used?

* [ ] 700
* [x] 7000
* [ ] 70000
* [ ] 700000

### Result

```text
Input tokens: 7111
Output tokens: 95
Cost: $0.00112365
```

### Notes

The exact number may vary between runs. The closest available answer is `7000`.

---

## Q3. Span timing

For a typical query, approximately how long does the LLM call take?

* [ ] Under 100 ms
* [ ] 100–500 ms
* [ ] 500–2000 ms
* [x] Over 2000 ms

### Result

```text
    "start_time": "2026-07-19T22:18:19.643759Z",
    "end_time": "2026-07-19T22:18:19.646159Z",

Search duration:

    "start_time": "2026-07-19T22:18:19.646662Z",
    "end_time": "2026-07-19T22:18:22.111248Z",

LLM duration: 22.111248 − 19.646662 = 2.464586 seconds = 2464.586 milliseconds
```

### Calculation

OpenTelemetry stores timestamps with nanosecond precision.

```python
duration_seconds = (end_time - start_time) / 1_000_000_000
```

When using the ISO timestamps from the console output, calculate the difference directly between the start and end times.

### Notes

Closest available answer is `Over 2000 ms`. The exact duration may vary between runs.

---

## Q4. Saving traces to SQLite

After replacing the console exporter with the custom SQLite exporter, which span names appear in the `spans` table?

* [ ] Only `rag`
* [ ] `rag` and `llm`
* [x] `rag`, `search`, and `llm`
* [ ] `search`, `llm`, and `judge`

### Result

```sql
SELECT DISTINCT name
FROM spans;
```

```text
Result:
     name
0  search
1     llm
2     rag
```

### Notes

The `spans` table contains three distinct span names: `rag`, `search`, and `llm`. The `judge` span is not present in the table.

---

## Q5. Querying trace data

After excluding the parent `rag` span and calculating the total duration for each remaining span type, which span takes the most total time?

* [ ] `search`
* [x] `llm`
* [ ] They are all about the same

### SQL query

```sql
SELECT name, start_time, end_time, (end_time - start_time) / 1000000.0 AS duration_ms
FROM spans
WHERE name != 'rag'
ORDER BY end_time - start_time DESC
LIMIT 5
```

### Result

```text
     name           start_time             end_time  duration_ms
0     llm  1784501245966275066  1784501249250618995  3284.343929
1  search  1784501245945348116  1784501245947830854     2.482738
```

### Notes

The `llm` span takes the most total time, followed by the `search` span.

---

## Q6. Token stability across runs

After running the same query four times, how much do the input-token counts vary?

* [x] They are identical
* [ ] Within 10% of each other
* [ ] Within 50% of each other
* [ ] They vary more than 50%

### SQL query

```sql
SELECT input_tokens
FROM spans
WHERE name = 'llm'
ORDER BY rowid DESC
LIMIT 4;
```

### Results

```text
  input_tokens
0          7111
1          7111
2          7111
3          7111
```

### Variation calculation

The input is simlar

### Result

```text
Minimum input tokens: 7111
Maximum input tokens: 7111
Variation: 0%
```

### Notes

That makes sense because the query, minsearch index, number of retrieved documents, and prompt construction are deterministic. The output tokens may still vary because the model response can differ.
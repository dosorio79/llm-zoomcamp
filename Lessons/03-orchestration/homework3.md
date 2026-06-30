# LLM Zoomcamp 2026 — Module 3 Homework: AI Orchestration with Kestra

> Homework template for Module 3.  
> Fill in the selected option and any notes/logged values after running the required Kestra flows.

## Repository Link

**Solution repository:** `<YOUR_GITHUB_REPO_LINK>`

---

## Question 1: Context Engineering

After trying the same prompt in ChatGPT vs Kestra's AI Copilot, what is the primary reason AI Copilot generates better Kestra flows?

**Options:**

- [ ] AI Copilot uses a more powerful model
- [x] AI Copilot has access to current Kestra plugin documentation
- [ ] AI Copilot uses more tokens
- [ ] AI Copilot has internet access

**Answer:** `<SELECTED_OPTION>`

**Notes / evidence:**

```text
When comparing the outputs, ChatGPT generated a generic flow with placeholders and lacked specific details about Kestra plugins. In contrast, AI Copilot produced a flow with accurate plugin references and configurations, demonstrating its access to up-to-date Kestra documentation.
```

---

## Question 2: RAG vs No RAG

Run both `1_chat_without_rag.yaml` and `2_chat_with_rag.yaml` in the Kestra UI. Read the execution logs for each.

The non-RAG response about Kestra 1.1 features is best described as:

**Options:**

- [ ] Accurate and specific, matching the actual release notes
- [x] Vague, generic, or fabricated — the model guesses from training data
- [ ] Empty — the model refuses to answer without context
- [ ] Identical to the RAG version

**Answer:** `<SELECTED_OPTION>`

**Notes / evidence:**

```text
<Add a short comparison of the non-RAG and RAG logs.>
```

---

## Question 3: Token usage — short summary

Run `4_simple_agent.yaml` with `summary_length = short` and leave the other inputs as defaults. Open the execution logs and find the token usage logged by the `log_token_usage` task.

What is the approximate **output** token count for `multilingual_agent`?

**Options:**

- [ ] 5-15 tokens
- [x] 60-100 tokens
- [ ] 200-400 tokens
- [ ] 500+ tokens

**Answer:** `<SELECTED_OPTION>`

**Logged value:** `<OUTPUT_TOKEN_COUNT>`

**Notes / evidence:**

```text
<Paste or summarize the relevant log line from log_token_usage.>
```

---

## Question 4: Token usage — long summary

Run `4_simple_agent.yaml` again with `summary_length = long`. Compare the `multilingual_agent` output token count to your result from Question 3.

Roughly how many times more output tokens does the long summary use?

**Options:**

- [ ] About the same (within 20%)
- [x] 2-5x more
- [ ] 10-20x more
- [ ] 50x more

**Answer:** `<SELECTED_OPTION>`

**Logged values:**
179
```text
Short summary output tokens: <SHORT_OUTPUT_TOKEN_COUNT>
Long summary output tokens:  <LONG_OUTPUT_TOKEN_COUNT>
Ratio:                       <LONG / SHORT>
```

**Notes / evidence:**

```text
<Paste or summarize the relevant log_token_usage lines.>
```

---

## Question 5: Modifying a flow

Open `4_simple_agent.yaml` in the Kestra flow editor. Find the `english_brevity` task and change its prompt from asking for exactly **1 sentence** to asking for exactly **3 sentences**. Save the flow, then run it with `summary_length = long`.

Compare the `english_brevity` output token count to the original 1-sentence version, also with `summary_length = long`.

How do they compare?

**Options:**

- [x] About the same (within 20%)
- [ ] 2-4x more
- [ ] 5-10x more
- [ ] 10x+ more

**Answer:** `<SELECTED_OPTION>`

**Logged values:**
190

```text
Original 1-sentence output tokens: 179
Modified 3-sentence output tokens: 190
Ratio:                            1.06
```

**Notes / evidence:**

```text
<Paste or summarize the relevant log_token_usage lines before and after the prompt change.>
```

---

## Question 6: Best Practices

Based on what you learned in this module, for production workflows requiring deterministic, repeatable results with strict compliance requirements, such as financial reporting or workflows in highly regulated industries, which approach is most appropriate?

**Options:**

- [ ] Always use AI agents for maximum flexibility and adaptation
- [x] Use traditional task-based workflows for predictability and auditability
- [ ] Use only RAG without agents for better performance
- [ ] Use web search tools exclusively to ensure current data

**Answer:** `<SELECTED_OPTION>`

**Notes / evidence:**

```text
<Add a short explanation based on the module concepts.>
```

---

## Optional: Learning in Public Post

### LinkedIn Draft

```text
Module 3 of LLM Zoomcamp by @DataTalksClub complete!

Just finished Module 3 - AI Orchestration with @Kestra.

Learned how to:

✅ Engineer context so the LLM gets the right information
✅ Ground answers in real data with RAG
✅ Build AI agents that decide which tools to call
✅ Orchestrate multi-agent systems

Here's my homework solution: <LINK>

Following along with this free course by @Alexey Grigorev.

You can sign up here: https://github.com/DataTalksClub/llm-zoomcamp/
```

### X / Twitter Draft

```text
Module 3 of LLM Zoomcamp done!

- AI orchestration with @kestra_io
- Context engineering
- RAG-grounded answers
- AI agents & multi-agent systems

My solution: <LINK>

Free course by @Al_Grigor & @DataTalksClub:
https://github.com/DataTalksClub/llm-zoomcamp/
```

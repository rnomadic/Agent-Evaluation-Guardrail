## This Repo is all about Agent Evaluation and Agentic Guardrail

### Evaluation Strategy for AI Agents
Enterprise adoption of autonomous AI agents is currently going through a trust and reliability crisis. To overcome this trust deficit, we take the first steps towards defining a comprehensive evaluation strategy for enterprise AI agents.

Unfortunately, it is a multi-faceted problem (illustrated in belwo fig) with the need to design validation tests covering both functional and non-functional aspects taking into account:

+ the underlying LLM (reasoning model),
+ solution architecture (retrieval-augmented generation — RAG, fine-tuning, agent/tool orchestration pattern, etc.),
+ applicable enterprise policies and AI regulations / responsible AI guidelines.

<br> <br>
<img width="1826" height="880" alt="image" src="https://github.com/user-attachments/assets/1ad95158-8b5b-4def-8b73-8605d9daece0" />
                                                <font color="grey">image credit: Debmalya Biswas</font>
<br> <br>
There are primarily 3 types of evaluation methodologies prevalent today:

#### 1. Generic benchmarks and datasets

Let us first consider publicly available LLM leaderboards, e.g., Hugging Face Open LLM Leaderboard. While useful, they primarily focus on testing pre-trained LLMs on generic NLP tasks (e.g., Q&A, reasoning, sentence completion) using public datasets, e.g.

SQuaD 2.0 — Q&A
Alpaca Eval — Instruction following
GLUE — Natural language understanding (NLU) tasks
MMLU — Multi-task language understanding
DecodingTrust — Responsible AI dimensions, the framework underlying HuggingFace’s LLM safety leaderboard
The key limitation here is that these leaderboards focus on assessing foundational (pre-trained) LLMs on generic natural language processing (NLP) tasks. Enterprise use-case contextualization entails further applying enterprise processes and data to fine-tune AI agents.


#### 2. LLM-as-a-Judge
#### 3. Manual evaluation


For item 2 and 3 please see the article [Agentic Evaluation & Guardrails](https://medium.com/@jyotir.bwn/agent-evaluation-20998fd25981)

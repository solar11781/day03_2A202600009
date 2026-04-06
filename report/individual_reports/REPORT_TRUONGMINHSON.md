# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Truong Minh Son
- **Student ID**: 2A202600331
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

As the **QA/Testing & Ops Lead**, my primary focus was ensuring system stability, environment portability, and reliable local inference. I architected the integration layer to ensure the ReAct loop could function in a "Zero-Cloud" environment.

- **Modules Implemented**: 
    - `src/core/local_provider.py`: Developed the core engine for GGUF model interaction, focusing on hardware-specific optimizations.
    - `main.py`: Created the central execution entry point using **Dependency Injection** to allow the agent to switch providers without code changes.
- **Ops & Documentation**: 
    - **Logic Mapping**: Designed the core **Flowchart logic** for the ReAct state machine to ensure deterministic transitions between Thinking and Acting.
    - **Reporting**: Authored the comprehensive **Group Report** and prepared the live demonstration environment to ensure a bug-free presentation.
- **Code Highlights**:
    Implemented a thread-safe initialization for `llama-cpp-python` to balance performance and system stability across different local hardware configurations:
    ```python
    self.llm = Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        n_threads=n_threads,
        verbose=False # Suppressing low-level C++ logs for a cleaner QA output
    )
    ```
- **Documentation**: My implementation follows the **Strategy Pattern**. By inheriting from `LLMProvider`, the `LocalProvider` ensures that the `ReActAgent` remains agnostic of the underlying model (OpenAI, Gemini, or Local), facilitating seamless regression testing across different backends.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: During the integration testing phase, the system consistently failed to initialize, throwing an `ImportError` that blocked the loading of the `LocalProvider` class.
- **Log Source**: `❌ Import Error: cannot import name 'LocalProvider' from 'src.core.llm_provider'`
- **Diagnosis (RCA)**: The root cause was a **Namespace Conflict** combined with stale metadata. The `main.py` entry point was incorrectly targeting the interface file instead of the implementation file. Additionally, from an Ops perspective, Python's `__pycache__` was retaining corrupted bytecode, causing the system to ignore manual code fixes during the rapid iteration phase.
- **Solution**: 
    1. **Namespace Correction**: Re-mapped the import hierarchy to `from src.core.local_provider import LocalProvider`.
    2. **Environment Patching**: Injected the project root into `sys.path` dynamically to resolve package discovery regardless of the user's terminal directory.
    3. **Cache Flushing**: Implemented a mandatory purge of all `__pycache__` directories to ensure a clean, deterministic build environment for the final demo.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: The `Thought` block acts as a **Chain-of-Thought (CoT)** buffer. In my tests, the Chatbot would often hallucinate a study schedule immediately. The ReAct Agent, however, used the `Thought` step to realize it lacked the current date and curriculum weights, triggering a search before answering.
2. **Reliability**: The Agent is significantly more reliable for **Fact-Contingent Tasks**. However, it performed worse on "Creative Writing" or "Simple Chat" where the overhead of the ReAct loop (extra tokens and latency) provided no functional benefit.
3. **Observation**: Environment feedback (Observations) provided a "Self-Correction" mechanism. If the search tool returned no results for a specific ML topic, the Agent used that failure to refine its next `Thought` and try an alternative query rather than giving up or lying.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Transition to **LangGraph** to allow for "Cyclic Graphs." This would enable the agent to revisit previous steps more efficiently than a linear loop.
- **Safety**: Implement **Pydantic Output Parsers** to validate that the LLM's `Action Input` is always a valid JSON schema before execution, preventing code-level crashes.
- **Performance**: Implement **KV-Caching** for the local model. Since the `SYSTEM_PROMPT` is sent with every turn of the ReAct loop, caching the prompt prefix would significantly reduce time-to-first-token (TTFT).

---

> [!NOTE]
> This report is submitted as part of the Lab 3 requirements for the Production-Grade Agentic System module.


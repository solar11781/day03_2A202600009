# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Bùi Trần Gia Bảo
- **Student ID**: 2A202600009
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

_Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.)._

- **Modules Implementated**:
  - `src/telemetry/logger.py` — implemented a structured JSON logger that writes per-day JSON-lines to `logs/` and supports console output via `LOG_TO_CONSOLE`.
  - `src/telemetry/metrics.py` — implemented `PerformanceTracker` (`tracker`) which records `LLM_METRIC` events, computes per-provider cost estimates, and exposes `track_request(...)` for providers to call.
  - `src/telemetry/analyze_logs.py` — refactored into reusable functions (`load_all_events`, `aggregate_metrics`, `write_evaluation_result`) and a CLI that writes `EVALUATION_RESULT.md`.
  - `src/telemetry/simulate_runs.py` — synthetic-run generator used for QA when a real model is not available.
  - `src/telemetry/chatbot_baseline.py` — small baseline entrypoint that calls the configured provider and logs `CHATBOT_RUN`/`CHATBOT_RESPONSE` events.
  - `src/agent/agent.py` — instrumented the `ReActAgent` to emit `AGENT_START`, `AGENT_STEP`, `TOOL_CALL`, `AGENT_ERROR`, and `AGENT_FINAL` events; added `run_id` support and passed `run_type='agent'` into provider calls.
  - `main.py` — updated to select LLM by `DEFAULT_PROVIDER` (uses `LocalProvider` when set to `local`) so local runs avoid remote quota problems.
  - `tests/test_agent_integration.py` — added an integration test that runs `main.main()` with injected mock providers and asserts `LLM_METRIC` and `AGENT_FINAL` appear in `logs/`.
  - Deleted redundant helper: `scripts/run_tests_quick.py` (removed to keep the workspace minimal).
- **Code Highlights**:

```python
logger.log_event("AGENT_STEP", {
                    "run_id": run_id,
                    "step": steps + 1,
                    "model": self.llm.model_name,
                    "action": action_name,
                    "content_preview": response_text[:300]
                })
```

- **Documentation**: The `ReActAgent.run()` loop now records structured telemetry for each Thought→Action cycle and for LLM usage. Providers call `tracker.track_request(...)` to emit `LLM_METRIC` events which are aggregated by `src/telemetry/analyze_logs.py` to produce concise evaluation outputs in `EVALUATION_RESULT.md`.

---

## II. Debugging Case Study (10 Points)

_Analyze a specific failure event you encountered during the lab using the logging system._

- **Problem Description**: When the user asked "Create a study plan from now to 30/04", the agent forwarded the short date string to tool(s). The `calendar` tool rejected the input because it expects a canonical date format (`YYYY-MM-DD` or `dd/mm/yyyy`), causing the agent to reach a dead-end while attempting to generate the schedule.

- **Relevant log excerpts**:

```json
{"timestamp":"2026-04-06T11:19:17.575292","event":"TOOL_CALL","data":{"run_id":"939eb2aa","tool":"calculate_date","args":"\"30/04 - current date\"","result":"25"}}
{"timestamp":"2026-04-06T11:19:55.651738","event":"TOOL_CALL","data":{"run_id":"939eb2aa","tool":"calendar","args":"\"Create a study plan from now to 30/04\", 25","result":"Error executing calendar: exam_date/start_date must be in dd/mm/yyyy or yyyy-mm-dd format"}}
```

- **Diagnosis**: The agent did not normalize short human-entered dates before calling the `calendar` tool. The `calculate_date` tool returned a numeric days value, but the `calendar` call still contained the raw `"30/04"` string, which the tool correctly rejected.

- **Proposed remediation**:
  - Add a deterministic pre-call normalizer (e.g., `normalize_date(arg: str) -> str`) that:
    - Detects short formats (DD/MM, D/M, DD-MM, D-M) and appends the current year to produce `YYYY-MM-DD`.
    - Expands two-digit years to four digits using a sensible cutoff (e.g., `00-49 -> 2000-2049`).
    - Validates the normalized date and, if ambiguous, prompts the user for clarification instead of forwarding invalid input.
    - Log both pre- and post-normalization values in the `TOOL_CALL` event metadata for auditable traces.
  - Add input-schema validation at the tool boundary for `calendar` and `task_planner` so invalid arguments are caught early and surfaced to the agent as an `InvalidFormat` error rather than letting the tool fail silently.
  - Update the system prompt to include a short rule: "When calling tools that accept dates, pass dates in ISO `YYYY-MM-DD`; if the user's date is incomplete, append the current year or ask for clarification."
  - Emit structured telemetry on format failures (e.g., `AGENT_ERROR` with `error_type: "InvalidFormat"` and the offending argument).
  - Add unit tests: `test_normalize_date()` (examples: `30/04` -> `2026-04-30`) and an integration test verifying the `calendar` tool receives an ISO date or that the agent asks the user when ambiguous.
  - Optionally: record a `normalized_args` field in `TOOL_CALL` events so the analyzer can quantify how often normalization is required.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

_Reflect on the reasoning capability difference._

1.  **Reasoning**: The explicit `Thought` block gives the agent a place to plan and decide which tool to call. In practical tasks (finding resources → computing days → scheduling), the ReAct loop prevented one-shot hallucinations by verifying results via tool outputs (`TOOL_CALL` events) and using them as observations for the next step.
2.  **Reliability**: The Agent incurs higher latency and token usage compared to a single-chat Chatbot. Aggregated results after the runs show:

```
Overall by run_type:
agent: count=8, avg_latency_ms=9158.2, avg_total_tokens=972.6
unknown: count=4, avg_latency_ms=4353.5, avg_total_tokens=381.0
```

This indicates: Agent uses ≈2.1× tokens and ≈2.1× latency vs the simpler chatbot/unknown runs in our test corpus. The tradeoff is structured tool usage and verifiable outputs at the cost of speed and token efficiency.

3.  **Observation**: Tool outputs (observations) materially changed next actions — e.g., `calculate_date` returned a numeric days value which the agent used to select `task_planner`/`calendar`. The `AGENT_STEP` events in `logs/2026-04-06.log` provide an audit trail showing how observations influenced subsequent actions.

---

## IV. Future Improvements (5 Points)

_How would you scale this for a production-level AI agent system?_

- **Scalability**: Replace synchronous tool calls with an async queue; batch repeated tool queries; add a cache layer for repeated resource lookups.
- **Safety**: Add an input schema and validator for each tool (enforce date formats, limits) and a supervisor LLM that audits actions before they are executed.
- **Performance**: Use quantized models (4-bit) for local deployments, enable token-level streaming for progress, and avoid re-sending long contexts when only a small update is needed.

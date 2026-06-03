```markdown
# Architectural Reflection & Failure Analysis

## 1. Initial Failures and Resolution
Early versions that relied strictly on prompt system instructions struggled with accurate boundary constraint checks. The LLM would frequently bypass missing prerequisite flags if the user query phrases sounded sufficiently eager. Moving this dependency into a hardcoded Python tool function (`check_prerequisites`) decoupled factual validation from model inference and eliminated hallucinated exceptions.

## 2. Guardrail Structural Integrity
Hard business rules (like academic probation tracking) cannot rely on non-deterministic LLM evaluation layers. The structural division here maps safe, deterministic filtering directly into Python routing before the model acts, keeping the agent focused purely on conversational routing.

## 3. Residual Risks
- **Context Capacity Limitations**: Pushing entire raw structural course data lists directly into context window variables is unsustainable at full production scales.
- **Race Conditions**: Because the application state relies entirely on memory values loaded at initialization time, multiple concurrent mutations during active scheduling choices would conflict without data locking abstractions.
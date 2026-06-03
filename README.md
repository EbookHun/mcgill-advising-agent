# McGill Course Advising Single-Agent System

This is a single-agent implementation built using the OpenAI Python SDK to handle academic advising under structural rules.

## State Strategy
- This application runs statelessly per execution. 
- Global variables representing student state and course parameters are dynamically passed into the execution loop during execution entry points.

## Guardrail Strategy
- **PROBATION_ESCALATION_RULE**: Executed at the code routing layer. If a student profile contains `academic_probation: True`, the application terminates inference pipelines and forces an immediate escalation block.
- **PREREQUISITE_CHECK_GUARD**: Managed by schema validation rules. If tool traces indicate a student lacks prerequisite courses, the agent sets `requires_human_approval = True`.

## Reproduction Steps
```bash
pip install openai pydantic
export OPENAI_API_KEY="your-api-key"
python app.py
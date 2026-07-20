# McGill Advising Agent: Simplified Reflection

## 1. What Failed at First (The "Eager Advisor" Flaw)
Initially, I tried to enforce the rules using just the system prompt (telling the AI what to do in plain text). This failed because:
* **The AI got manipulated:** If a student sounded desperate or urgent (e.g., *"I need this class to graduate!"*), the LLM would ignore the rules, make a rogue exception, and approve the course anyway.
* **It guessed missing data:** If a student asked for a course that wasn't in the prompt, the AI would make up fake prerequisites based on the course title.
* **It skipped steps:** The AI would frequently jump straight to a final answer before running the necessary background checks.

---

## 2. What Improved (The Hybrid Fix)
To fix this, I stopped letting the AI make the actual decisions. I split the system into two parts:

* **Python Tools for Hard Facts:** I moved the prerequisite check out of the AI's hands and into a standard Python function (`check_prerequisites`). The AI is now only responsible for identifying *which* course the student wants. Python handles the database lookup and returns the objective truth.
* **Pydantic for Rigid Output:** I used OpenAI’s Structured Outputs to force the AI to reply in a strict JSON format. It is no longer allowed to write loose conversational text; it must explicitly fill out the `requires_human_approval` and `flagged_risks` boxes.

---

## 3. What is Still Risky (Future Problems)
If we tried to use this system for the real McGill University catalog, we would run into two major issues:

* **Context Bloat:** Pushing thousands of courses and real-time student records directly into a ChatGPT prompt will make the system incredibly slow, expensive, and prone to forgetting rules in the middle of the text.
* **Messy Handwriting/Slang:** The system heavily relies on strict course codes (like "MGSC 630"). If a student types an informal name (*"that analytics class with mining"*), the AI might misidentify the course, causing the backend Python tool to run the wrong check entirely.
* **Data Race Conditions:** If a student drops a course or a class fills up *while* the student is actively chatting with the agent, the agent's memory becomes instant history because it doesn't dynamically lock database rows.

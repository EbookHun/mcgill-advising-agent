🚀 Starting Advising Agent Evaluation Suite...
==================================================

📌 Running EVAL_01 (Happy Path)
User Input: 'Can I take MGSC 613 and BUSA 650?'
Traceback (most recent call last):
  File "C:\Users\ibuku\mcgill_advisor_system\app.py", line 166, in <module>
    res = run_advising_agent(case['request'], case['profile'])
  File "C:\Users\ibuku\mcgill_advisor_system\app.py", line 114, in run_advising_agent
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
    ...<2 lines>...
        tool_choice="auto"
    )
  File "C:\Users\ibuku\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\openai\resources\chat\completions\completions.py", line 177, in parse
    chat_completion_tools = _validate_input_tools(tools)
  File "C:\Users\ibuku\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\openai\lib\_parsing\_completions.py", line 79, in validate_input_tools
    raise ValueError(
        f"`{tool['function']['name']}` is not strict. Only `strict` function tools can be auto-parsed"
    )
ValueError: `search_courses` is not strict. Only `strict` function tools can be auto-parsed
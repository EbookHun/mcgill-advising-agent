import json
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI

client = OpenAI()

# 1. FIXTURES
COURSE_CATALOG = {
    "MGSC 613": {"name": "Linear Optimization", "prereqs": []},
    "MGSC 624": {"name": "Predictive Analytics", "prereqs": []},
    "MGSC 630": {"name": "Simulation & Optimization", "prereqs": ["MGSC 613"]},
    "MGSC 640": {"name": "Tech Analytics & Text Mining", "prereqs": ["MGSC 624"]},
    "BUSA 650": {"name": "GTM & Brand Strategy", "prereqs": []},
}

STUDENT_PROFILE = {
    "name": "Alex Adeleye",
    "completed_courses": ["MGSC 613"],
    "max_credits": 12,
    "academic_probation": False
}

POLICY_RULES = """
1. Credit Limit: Maximum of 12 credits (4 courses) per semester.
2. Prerequisite Rule: Students cannot take a course unless its prereqs are in completed_courses.
3. Probation Rule: If academic_probation is True, maximum credits allowed is 6, and human advisor sign-off is MANDATORY.
"""

# 2. STRUCTURED OUTPUT SCHEMAS
class RecommendationDetail(BaseModel):
    course_code: str
    reasoning: str

class AdvisorResponse(BaseModel):
    recommended_courses: List[RecommendationDetail] = Field(description="List of approved and recommended courses.")
    flagged_risks: List[str] = Field(description="Any prerequisite violations, credit overloads, or policy risks found.")
    requires_human_approval: bool = Field(description="Set to True if any guardrails or policy escalations are triggered.")
    approval_reason: Optional[str] = Field(description="The explicit reason why human approval is required.")

# 3. TYPED TOOLS
def search_courses() -> str:
    """Returns the available course catalog and descriptions."""
    return json.dumps(COURSE_CATALOG, indent=2)

def check_prerequisites(course_code: str) -> str:
    """Checks if the student meets the prerequisites for a given course code."""
    course = COURSE_CATALOG.get(course_code)
    if not course:
        return json.dumps({"error": "Course not found"})
    required = course["prereqs"]
    missing = [p for p in required if p not in STUDENT_PROFILE["completed_courses"]]
    return json.dumps({
        "course": course_code,
        "met": len(missing) == 0,
        "missing_prerequisites": missing
    })

tools_definition = [
    {
        "type": "function",
        "function": {
            "name": "search_courses",
            "description": "Get the list of available courses and their prerequisites.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_prerequisites",
            "description": "Check if a student meets the requirements to take a specific course.",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_code": {"type": "string", "description": "The course code, e.g., MGSC 630"}
                },
                "required": ["course_code"]
            }
        }
    }
]

# 4. AGENT RUNNER LOOP WITH GUARDRAILS
def run_advising_agent(user_request: str, profile_override: Optional[dict] = None) -> AdvisorResponse:
    current_profile = profile_override or STUDENT_PROFILE
    
    # Hard Guardrail (Bypasses LLM processing entirely if true)
    if current_profile.get("academic_probation", False):
        return AdvisorResponse(
            recommended_courses=[],
            flagged_risks=["CRITICAL: Student is currently on Academic Probation."],
            requires_human_approval=True,
            approval_reason="PROBATION_ESCALATION_RULE: Mandatory human advisor review required for students on probation."
        )

    system_prompt = f"""
    You are an expert academic advisor agent for McGill University.
    STUDENT PROFILE: {json.dumps(current_profile, indent=2)}
    POLICY RULES: {POLICY_RULES}
    
    CRITICAL INSTRUCTIONS:
    1. Always use 'search_courses' to check availability.
    2. Always use 'check_prerequisites' before finalizing recommendations.
    3. If prerequisites are missing, flag it in risks and set requires_human_approval to True.
    4. If requests exceed credit limits (more than 4 courses), flag it and set requires_human_approval to True.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_request}
    ]

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools_definition,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    
    if response_message.tool_calls:
        messages.append(response_message)
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "search_courses":
                tool_output = search_courses()
            elif function_name == "check_prerequisites":
                tool_output = check_prerequisites(function_args.get("course_code"))
            else:
                tool_output = json.dumps({"error": "Unknown tool"})
                
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": tool_output
            })
            
        final_response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=messages,
            response_format=AdvisorResponse
        )
        return final_response.choices[0].message.parsed
        
    return response_message.parsed

# 5. TEST SUITE / EVALUATION LOOP
if __name__ == "__main__":
    print("🚀 Starting Advising Agent Evaluation Suite...\n" + "="*50)
    
    eval_cases = [
        {"id": "EVAL_01 (Happy Path)", "request": "Can I take MGSC 613 and BUSA 650?", "profile": None},
        {"id": "EVAL_02 (Valid Prereq Path)", "request": "I want to sign up for MGSC 630.", "profile": None},
        {"id": "EVAL_03 (Missing Prereq Violation)", "request": "I want to take MGSC 640.", "profile": None},
        {"id": "EVAL_04 (Credit Overload)", "request": "Sign me up for MGSC 613, MGSC 624, MGSC 630, MGSC 640, and BUSA 650.", "profile": None},
        {"id": "EVAL_05 (Probation Guardrail)", "request": "I just want to take BUSA 650.", "profile": {**STUDENT_PROFILE, "academic_probation": True}}
    ]
    
    for case in eval_cases:
        print(f"\n📌 Running {case['id']}\nUser Input: '{case['request']}'")
        res = run_advising_agent(case['request'], case['profile'])
        print(f"Outputs JSON:\n{res.model_dump_json(indent=2)}")
        print("-" * 50)
import chainlit as cl
from dotenv import load_dotenv
import instructor
from openai import OpenAI
import os
import json

load_dotenv()

# Patch the OpenAI client with Instructor
client = instructor.from_openai(OpenAI(api_key=os.environ['OPENAI_API_KEY']))

# Define prompt templates
PRD_PROMPT_TEMPLATE = """
### Product Requirements Document (PRD) for AI Applications

#### Introduction
- **Objective/Goal**: 
  - Explain the purpose of the AI application and what it aims to achieve.
  - Provide a high-level overview of the release purpose.
  - User Proposal: {user_proposal}

#### Features
- **Feature 1**: 
  - **Description**: Detailed description of the feature.
  - **Goal**: What this feature aims to achieve.
  - **Use Case**: Example of how a user would utilize this feature.
  - **Additional Details**: Specifics such as out-of-scope items and prompt structure.
  
- **Feature 2**: 
  - **Description**: Detailed description of the feature.
  - **Goal**: What this feature aims to achieve.
  - **Use Case**: Example of how a user would utilize this feature.
  - **Additional Details**: Specifics such as out-of-scope items and prompt structure.

*(Repeat for each feature)*

#### UX Flow & Design Notes
- **Overview**: General guidance required to ensure the release objectives are met.
- **User Workflow**: Describe the overall user workflow.
- **Design Considerations**: Any specific design notes relevant at this stage.

#### System & Environment Requirements
- **Supported Environments**: 
  - Browsers (e.g., Chrome, Firefox, Safari)
  - Operating Systems (e.g., Windows 10, macOS)
  - Memory and Processing Power requirements

#### Assumptions, Constraints & Dependencies
- **Assumptions**: 
  - List anything expected to be in place (e.g., all users will have Internet connectivity).
  
- **Constraints**: 
  - Dictate limits for the implementation (e.g., budgetary constraints, technical limitations).
  
- **Dependencies**: 
  - Conditions or items the product will rely on (e.g., relying on Google Maps for directions).

#### Prompt Engineering Practices
- **Ambiguity Mitigation**: Ensure clear, specific prompts to avoid ambiguous outputs. Evaluate prompts using examples and test consistency with different inputs.
- **Versioning**: Track and version each prompt to monitor performance changes over time.
- **Optimization**: Apply techniques like chain-of-thought prompting, majority voting, and breaking tasks into smaller prompts to improve output quality.
- **Cost & Latency Management**: Balance detailed prompts with cost efficiency and manage latency by optimizing token usage.

#### Task Composability
- **Multiple Tasks Composition**: Outline how multiple tasks interact, including sequential and parallel executions, and control flows like if statements and loops.
- **Agents and Tools**: Describe the use of agents to manage tasks and the integration of tools such as SQL executors and web browsers.
- **Control Flows**: Detail the use of control flows in managing tasks, including sequential, parallel, if statements, and loops.

#### Review & Approval Process
- **Initial Review**: 
  - Steps for internal product team review.
  - Feedback incorporation.
  
- **Business Side Stakeholders Review**: 
  - Process for aligning with business stakeholders.
  
- **Engineering Handoff**: 
  - Clarifications and updates based on technical team feedback.
  
- **Final Approval**: 
  - Ensuring no surprises later on.
  - Agreement from all teams involved (UX design, engineering, QA).

---

This PRD template is configured specifically for the user proposal: "{user_proposal}", ensuring a consistent format for every PRD, covering all necessary aspects from features to dependencies, review processes, and incorporating best practices in prompt engineering and task composability.
"""

DESIGNER_PROMPT_TEMPLATE = """
<System Message>
You are the Engineer/Designer Agent responsible for creating a functional product.
For a given proposal and PRD, write the simplest python script to quickly test your PoC. Only output python code and markdown.
</System Message>
\n<>####<>\n
<Context>
Proposed PRD:
{prd_response_raw}
\n<>####<>\n
Proposed PRD in its pydantic class form:
{prd_json}
</Context>
\n<>####<>\n
<Original User Proposal>
Original User Proposal:
{user_proposal}
</Original User Proposal>
\n<>####<>\n
<Instruction>
Guide the following instructions with the above system message and above context specifications as well as the original user proposal.
Write a simple AI application development plan for the user with as few steps as possible. Do not be verbose and explain the plan in an elementary school level.
The instructions to develop this Proof of Concept Implementation should only take one engineer about a day or two to complete.
Make sure what you are suggesting exist, so for each suggestion think step by step why you are suggesting it and how to find resources for that component.
Go to the below link, read it and use it as a reference guide for starting out:
https://raw.githubusercontent.com/AI-Maker-Space/Beyond-ChatGPT/main/README.md
</Instruction>
\n<>####<>\n
"""

# Function to format the templates with provided variables
def format_template(template, **kwargs):
    return template.format(**kwargs)

# Define functions
def llm_call(user_prompt, system_prompt=None):
    print("Calling LLM...")  # Debug print
    if system_prompt:
        print("Using system prompt...")  # Debug print

    messages = [
        {"role": "user", "content": user_prompt}
    ] if system_prompt is None else [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_model=None,
        messages=messages,
    )
    print("LLM response received.")  # Debug print
    return response

# Define the Chainlit message handler
@cl.on_message
async def main(message: cl.Message):

    print("Received message.")  # Debug print
    user_proposal = message.content

    prd_sys1 = format_template(PRD_PROMPT_TEMPLATE, user_proposal=user_proposal)
    prd_response_raw = llm_call(user_prompt=user_proposal, system_prompt=prd_sys1).choices[0].message.content
    print("PRD response generated.")  # Debug print

    prd_json = json.dumps({"objective_goal": "Develop a chatbot...", "features": [], "ux_flow_design_notes": "...", "system_environment_requirements": "...", "assumptions": [], "constraints": [], "dependencies": [], "prompt_engineering_practices": "...", "task_composability": "...", "review_approval_process": "..."})
    designer_prompt = format_template(DESIGNER_PROMPT_TEMPLATE, prd_response_raw=prd_response_raw, prd_json=prd_json, user_proposal=user_proposal)
    designer_output = llm_call(designer_prompt).choices[0].message.content
    print("Designer output received.")  # Debug print

    print("Sending messages to Chainlit UI...")  # Debug print

    await cl.Message(content=f"Generated PRD:\n{prd_response_raw}").send()
    print("Generated PRD message sent.")  # Debug print

    await cl.Message(content=f"Designer Output:\n{designer_output}").send()
    print("Designer output message sent.")  # Debug print


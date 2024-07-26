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

    messages = [
        {"role": "user", "content": user_prompt}
    ] if system_prompt is None else [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    return client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_model=None,
        messages=messages,
    )

# Define the Chainlit message handler
@cl.on_chat_start
async def start():

    # Welcome message
    wel_msg = cl.Message(content="Welcome to Build Advisor!\n\nBuild Advisor creates plan, production requirement spec and implementation for your AI application idea.\nQuickly create a PoC so you can determine whether an idea is worth starting, worth investing time and/or money in.")
    await wel_msg.send()

    # Ask user for AI application / business idea
    res = await cl.AskUserMessage(content="What is your AI application/business idea?", timeout=30).send()
    if res:
        await wel_msg.remove()
        # print(res['output'])
        await cl.Message(
            content=f"User Proposal: {res['output']}.\n\nStarting...",
        ).send()

        user_proposal = res['output']

        prd_sys1 = format_template(PRD_PROMPT_TEMPLATE, user_proposal=user_proposal) # system message to create PRD
        prd_response_raw = llm_call(user_prompt=user_proposal, system_prompt=prd_sys1).choices[0].message.content # get PRD from LLM

        # send PRD output to UI
        prd_msg = cl.Message(content=prd_response_raw)
        await prd_msg.send()

        prd_json = json.dumps({"objective_goal": "Develop a chatbot...", "features": [], "ux_flow_design_notes": "...", "system_environment_requirements": "...", "assumptions": [], "constraints": [], "dependencies": [], "prompt_engineering_practices": "...", "task_composability": "...", "review_approval_process": "..."})
        designer_prompt = format_template(DESIGNER_PROMPT_TEMPLATE, prd_response_raw=prd_response_raw, prd_json=prd_json, user_proposal=user_proposal)
        designer_output = llm_call(designer_prompt).choices[0].message.content

        designer_output_msg = cl.Message(content=designer_output)
        await designer_output_msg.send()
        # designer_output_msg.content = prd_msg.content + "\n###\n" + designer_output_msg.content

        # update outputs in UI
        for secs in [1,5,10,20]:
            await cl.sleep(secs)
            await prd_msg.update()
            await designer_output_msg.update()


####
# TO DO:
# - output message as download
# - have follow up messages revise the original output or give feedback
####


# # on message just does the same but gets hung up...
# @cl.on_message
# async def main(message: cl.Message):

#     print("Received message.")  # Debug print
#     user_proposal = message.content

#     llm_running = cl.Message(content="LLM running...")
#     await llm_running.send()

#     prd_sys1 = format_template(PRD_PROMPT_TEMPLATE, user_proposal=user_proposal) # system message to create PRD
#     prd_response_raw = llm_call(user_prompt=user_proposal, system_prompt=prd_sys1).choices[0].message.content # get PRD from LLM

#     # prd_sys1 = "temp sys message"
#     # prd_response_raw = "temp prd message"
#     # prd_response_raw = llm_call(user_prompt=user_proposal, system_prompt=prd_sys1).choices[0].message.content # get PRD from LLM

#     # await llm_running.remove()

#     # send PRD output to UI
#     prd_sys_msg = cl.Message(content=f"prd_sys1: {prd_sys1}")
#     # await prd_sys_msg.send()
#     # await prd_sys_msg.remove()
    
#     # prd_msg = cl.Message(content=f"prd_response_raw: {prd_response_raw}")
#     prd_msg = cl.Message(content=prd_response_raw)
#     await prd_msg.send()
#     # prd_msg = cl.Message(content=prd_response_raw)
#     # await prd_msg.update()

#     prd_json = json.dumps({"objective_goal": "Develop a chatbot...", "features": [], "ux_flow_design_notes": "...", "system_environment_requirements": "...", "assumptions": [], "constraints": [], "dependencies": [], "prompt_engineering_practices": "...", "task_composability": "...", "review_approval_process": "..."})
#     designer_prompt = format_template(DESIGNER_PROMPT_TEMPLATE, prd_response_raw=prd_response_raw, prd_json=prd_json, user_proposal=user_proposal)
#     designer_output = llm_call(designer_prompt).choices[0].message.content
#     # print(designer_output)
#     designer_output_msg = cl.Message(content=designer_output)
#     await designer_output_msg.send()
#     await cl.sleep(1)
#     designer_output_msg.content = prd_msg.content + "\n###\n" + designer_output_msg.content
#     await designer_output_msg.update()

#     # print("Sending messages to Chainlit UI...")  # Debug print

#     # await cl.Message(content=f"Generated PRD:\n{prd_response_raw}").send()

# Load the starters ... overrided by on_chat_start
import starters
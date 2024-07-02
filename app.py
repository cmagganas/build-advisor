import chainlit as cl
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import instructor
from openai import OpenAI
import os

load_dotenv()

# Patch the OpenAI client with Instructor
client = instructor.from_openai(OpenAI(api_key=os.environ['OPENAI_API_KEY']))

# Define the Pydantic models
class UserProposal(BaseModel):
    proposal: str = Field(description="This is the proposal of the original user prompt. It should be a clear concise detailed plan to use simple ai software tools to solve specific problem.")
    is_clear: str = Field(description="Is the proposed plan clear? It specifies which tools it needs to use and how. It lays out each component and how they all connect.")
    is_detailed: str = Field(description="Is the proposed plan detailed? Each component should have a description of what it does.")
    is_explicit: str = Field(description="Is the proposed plan explicit? Each component should have a data model to describe their input and output schema.")

class ProposedArchitecture(BaseModel):
    proposed_architecture: str = Field(description="A detailed AI application architecture with all the tools required for the plan proposed. (e.g. Python packages)")

class PropositionWithRevision(BaseModel):
    revised_proposed_architecture: str = Field(description="Step by step implementation of software solution.")

# Define functions
def extract_user_proposal_details(user_proposal: str) -> UserProposal:
    return client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_model=UserProposal,
        messages=[
            {"role": "user", "content": user_proposal},
        ],
    )

def generate_proposed_architecture(proposal: str) -> ProposedArchitecture:
    return client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_model=ProposedArchitecture,
        messages=[
            {"role": "user", "content": f"Write a detailed AI application architecture with all the tools required for the plan proposed: \n\n{proposal}"},
        ],
    )

def revise_architecture(proposed_architecture: str) -> PropositionWithRevision:
    return client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_model=PropositionWithRevision,
        messages=[
            {"role": "user", "content": f"Revise the plan proposed: \n\n{proposed_architecture}\n\nThe plan should be a step by step implementation of software solution."},
        ],
    )


# Define the Chainlit message handler
@cl.on_message
async def main(message: cl.Message):

    user_proposal = message.content

    user_proposal_details = extract_user_proposal_details(user_proposal)
    
    proposed_architecture = generate_proposed_architecture(user_proposal_details.proposal)
    
    await cl.Message(
        content=f"Proposed Architecture:\n{proposed_architecture.proposed_architecture}"
    ).send()

    feedback_message = await cl.AskUserMessage(content="What do you think about this proposed plan and alleged architecture?", timeout=60).send()
    if feedback_message:
        human_feedback_of_proposed_plan = feedback_message["output"]
    
        revised_architecture = revise_architecture(proposed_architecture.proposed_architecture)
    
        await cl.Message(
            content=f"Revised Architecture:\n{revised_architecture.revised_proposed_architecture}"
        ).send()

        with open("output.md", "w") as output_file:
            output_file.write("# User Proposal\n")
            output_file.write(user_proposal_details.proposal + "\n\n")
            output_file.write("# Proposed Architecture\n")
            output_file.write(proposed_architecture.proposed_architecture + "\n\n")
            output_file.write("# Revised Architecture\n")
            output_file.write(revised_architecture.revised_proposed_architecture + "\n")

        await cl.Message(
            content="The results have been saved to output.md"
        ).send()

# Load the starters
import starters

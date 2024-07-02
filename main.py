import instructor
from openai import OpenAI
import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Patch the OpenAI client with Instructor
client = instructor.from_openai(OpenAI(api_key=os.environ['OPENAI_API_KEY']))

# Function to extract user details
class UserProposal(BaseModel):
    proposal: str = Field(description="This is the proposal of the original user prompt. It should be a clear concise detailed plan to use simple ai software tools to solve specific problem.")
    is_clear: str = Field(description="Is the proposed plan clear? It specifies which tools it needs to use and how. It lays out each component and how they all connect.")
    is_detailed: str = Field(description="Is the proposed plan detailed? Each component should have a description of what it does.")
    is_explicit: str = Field(description="Is the proposed plan explicit? Each component should have a data model to describe their input and output schema.")

def extract_user_proposal_details(user_proposal) -> UserProposal:
    return client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_model=UserProposal,
        messages=[
            {"role": "user", "content": user_proposal},
        ],
    )

# Function to generate proposed architecture
class ProposedArchitecture(BaseModel):
    proposed_architecture: str = Field(description="A detailed AI application architecture with all the tools required for the plan proposed. (e.g. Python packages)")

def generate_proposed_architecture(proposal: str) -> ProposedArchitecture:
    return client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_model=ProposedArchitecture,
        messages=[
            {"role": "user", "content": f"Write a detailed AI application architecture with all the tools required for the plan proposed: \n\n{proposal}"},
        ],
    )

# Function to revise architecture
class PropositionWithRevision(BaseModel):
    revised_proposed_architecture: str = Field(description="Step by step implementation of software solution.")

def revise_architecture(proposed_architecture: str) -> PropositionWithRevision:
    return client.chat.completions.create(
        model="gpt-4-turbo-preview",
        response_model=PropositionWithRevision,
        messages=[
            {"role": "user", "content": f"Revise the plan proposed: \n\n{proposed_architecture}\n\nThe plan should be a step by step implementation of software solution."},
        ],
    )

def main():  # sourcery skip: extract-method
    user_proposal = input("Please enter the AI app you'd like to develop and the problem you are trying to solve: ")
    user_proposal_details = extract_user_proposal_details(user_proposal)
    
    proposed_architecture = generate_proposed_architecture(user_proposal_details.proposal)
    
    print("Proposed Architecture:")
    print(proposed_architecture.proposed_architecture)
    
    human_feedback_of_proposed_plan = input("What do you think about this proposed plan and alleged architecture?: ")
    
    revised_architecture = revise_architecture(proposed_architecture.proposed_architecture)
    
    print("Revised Architecture:")
    print(revised_architecture.revised_proposed_architecture)
    
    with open("outputs/output.md", "w") as output_file:
        output_file.write("# User Proposal\n")
        output_file.write(user_proposal_details.proposal + "\n\n")
        output_file.write("# Proposed Architecture\n")
        output_file.write(proposed_architecture.proposed_architecture + "\n\n")
        output_file.write("# Revised Architecture\n")
        output_file.write(revised_architecture.revised_proposed_architecture + "\n")

if __name__ == "__main__":
    main()

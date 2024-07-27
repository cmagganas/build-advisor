import chainlit as cl
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI
import os
import json

load_dotenv()

# Async OpenAI
client = AsyncOpenAI(api_key=os.environ['OPENAI_API_KEY'])

async def llm_call(user_prompt, system_prompt=None):
    # sourcery skip: inline-immediately-returned-variable
    chat_completion = await client.chat.completions.create(
      messages = [
          {"role": "user", "content": user_prompt}
      ] if system_prompt is None else [
          {"role": "system", "content": system_prompt},
          {"role": "user", "content": user_prompt},
      ],
      model="gpt-4o-mini"
    )
    return chat_completion


# Define prompt templates
PRD_PROMPT_TEMPLATE = """
### Product Requirements Document (PRD) for AI Applications

User Proposal: {user_proposal}

To generate a comprehensive Product Requirement Document (PRD) for your AI application, please provide detailed responses to the following prompts. The sections in **bold** are particularly important, and those marked with **[!]** are critical to get right. These sections should be prioritized in your responses and the generated PRD.

1. **Product Name and Brief Description:**
   - What is the name of your AI application?
   - Provide a brief description (1-2 sentences) of your product.

2. **Primary Problem:**
   - What is the main problem your AI application aims to solve?
   - Why is this problem significant?

3. **Target Audience or User Base:**
   - Who are the primary users of your AI application?
   - Describe their key characteristics and needs.

4. **Key Features:**
   - List 3-5 key features you want to include in your AI application.
   - Explain the importance of each feature.

5. **Technical Requirements or Constraints:**
   - Are there any specific technical requirements or constraints for your application?
   - Include details about platforms, technologies, or integrations needed.

6. **Development and Launch Timeline:**
   - What is the expected timeline for development and launch?
   - Include any important milestones.

Based on the information provided, the LLM will generate a comprehensive PRD following the structure outlined below. Prioritize and ensure thorough and accurate information in the **bold** sections and especially those marked with **[!]**:

1. **Overview**
   - **Problem Statement**
     - The Problem Space section outlines the key challenges and issues that the product aims to address. It includes an analysis of the current limitations, pain points, and gaps in the existing solutions, providing a clear understanding of why the new product is necessary.
   - **Proposed Solution**
     - The Proposed Solution section describes the envisioned product and how it intends to solve the identified problems. It highlights the core functionalities, innovative features, and unique selling points that differentiate it from existing solutions.
   - **Features Advantages**
     - Highlights focus on the key advantages and positive aspects of the proposed solution. This includes major features, benefits to the users, expected improvements in user experience, and competitive advantages.
   - **Feature Challenges**
     - Challenges address the potential obstacles, limitations, and risks associated with the proposed solution. This section provides a realistic view of what might go wrong, areas that need careful attention, and any trade-offs made in the design and implementation of the product.

2. **Strategic Context**
   - **User Needs**
     - User Needs identify and analyze the key requirements and pain points of the target users. This section provides detailed user personas, usage scenarios, and key features that users expect from the product. Understanding user needs is crucial for aligning the product development process with user expectations and delivering a solution that addresses real problems.
   - **Business Driver**
     - The Business Driver section outlines the primary business motivations behind developing the product. This includes strategic goals, revenue targets, market expansion, customer retention, and competitive advantages. It links the product's objectives to the broader business strategy, ensuring alignment and support from stakeholders.
   - **[!] Research, Market Analysis, and Competitive Benchmarking**
     - This section presents comprehensive research on market trends, user behavior, and industry standards. It includes competitive benchmarking to analyze the strengths and weaknesses of current market players and identify opportunities for differentiation. Market analysis helps in understanding the competitive landscape and positioning the product effectively.
   - Current Product Analysis:
     - The Current Product Analysis reviews the existing products and solutions within the organization and the market. It identifies gaps, overlaps, and areas for improvement. This section provides insights into what works well and what needs enhancement, guiding the development of new features and functionalities.
   - **[!] Product Growth**
     - Product Growth outlines the potential for the product to scale and expand. This includes projections for user adoption, market penetration, and revenue growth. It also addresses strategies for sustaining long-term growth, such as feature updates, new market entries, and partnerships.
   - **[!] Brand Alignment**
     - Brand Alignment ensures that the product's development and marketing strategies are consistent with the company's brand values and identity. This section discusses how the product will enhance the brand's reputation, align with brand messaging, and leverage brand equity to attract users.
   - **[!] Roadmap**
     - The Roadmap provides a high-level timeline and milestones for product development and launch. It outlines key phases, deliverables, and deadlines, helping to manage expectations and ensure timely execution. The roadmap is essential for coordinating efforts across different teams and keeping the project on track.

3. **Product Definition**
   - **Functional Requirements**
     - Functional requirements describe the specific behaviors, features, and functionalities the product must have. These requirements define what the system should do and include detailed descriptions of each feature.
   - **Non-Functional Requirements**
     - Non-functional requirements specify the quality attributes, system performance, and operational constraints of the product. These requirements ensure that the system operates effectively and efficiently.
   - User Stories:
     - User stories are short, simple descriptions of a feature told from the perspective of the end user. They help to capture the functional requirements in a way that is easy to understand and relate to.
   - User Experience:
     - The User Experience section focuses on the design and interaction aspects of the product. It includes wireframes, mockups, and user flow diagrams to illustrate how users will interact with the system.

4. **Data**
   - Data Source (ETL):
     - The Data Source (ETL) section describes the processes for extracting, transforming, and loading data from various sources. This includes identifying the data sources, defining the extraction methods, detailing the transformation processes, and explaining how the data will be loaded into the system for use by the AI models.
   - Feature Data Collection:
     - Feature Data Collection focuses on how data will be collected to create and refine the AI features. This involves identifying the types of data needed, defining the collection methods, and ensuring data quality and relevance.
   - Features Metrics:
     - Feature Metrics define the key performance indicators (KPIs) and other metrics used to measure and analyze the performance of the AI feature. These metrics help in evaluating the effectiveness, efficiency, and impact of the feature.

5. **Acceptance Criteria**
   - **Accuracy**
     - The extent to which the AI model's outputs align with expected results. The level of importance and a score to achieve and how it's measured.
   - **Performance/Latency**
     - The speed and efficiency of the AI application, minimizing response times. SLAs on acceptable performance based on the target environment.
   - Cost @ Scale:
     - Scale and cost criteria assess the AI application's ability to handle increased load. Growth plan including DevOps, OPEX, and location.
   - KPIs:
     - Product-specific feature key performance indicators to grade health over time. Customer satisfaction rating and feedback.

6. **Challenges and Considerations**
   - Risks:
     - Identification and analysis of potential risks. Impact assessment and mitigation strategies.
   - Innovations:
     - Innovative features and technologies being integrated. Potential challenges and benefits of these innovations.
   - Dependencies:
     - Internal and external dependencies critical to the project. Plans to manage and mitigate dependency-related issues.
   - Events:
     - Key events that could impact the project timeline or scope. Strategies to manage and leverage these events.
   - Contingency Plans:
     - Contingency strategies for managing unforeseen issues. Backup plans for critical project components.

7. **Conclusion**
   - Summary:
     - Including key next steps.

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

# Example PRD Schema (JSON)
PRD_JSON_TEMPLATE = json.dumps({
    "user_proposal": "Develop a chatbot...",
    "overview": {
        "problem_statement": "The Problem Space section outlines the key challenges and issues that the product aims to address...",
        "proposed_solution": "The Proposed Solution section describes the envisioned product and how it intends to solve the identified problems...",
        "features_advantages": "Highlights focus on the key advantages and positive aspects of the proposed solution...",
        "feature_challenges": "Challenges address the potential obstacles, limitations, and risks associated with the proposed solution..."
    },
    "strategic_context": {
        "user_needs": "User Needs identify and analyze the key requirements and pain points of the target users...",
        "business_driver": "The Business Driver section outlines the primary business motivations behind developing the product...",
        "research_market_analysis_and_competitive_benchmarking": "This section presents comprehensive research on market trends, user behavior, and industry standards...",
        "current_product_analysis": "The Current Product Analysis reviews the existing products and solutions within the organization and the market...",
        "product_growth": "Product Growth outlines the potential for the product to scale and expand...",
        "brand_alignment": "Brand Alignment ensures that the product's development and marketing strategies are consistent with the company's brand values and identity...",
        "roadmap": "The Roadmap provides a high-level timeline and milestones for product development and launch..."
    },
    "product_definition": {
        "functional_requirements": "Functional requirements describe the specific behaviors, features, and functionalities the product must have...",
        "non_functional_requirements": "Non-functional requirements specify the quality attributes, system performance, and operational constraints of the product...",
        "user_stories": "User stories are short, simple descriptions of a feature told from the perspective of the end user...",
        "user_experience": "The User Experience section focuses on the design and interaction aspects of the product..."
    },
    "data": {
        "data_source_etl": "The Data Source (ETL) section describes the processes for extracting, transforming, and loading data from various sources...",
        "feature_data_collection": "Feature Data Collection focuses on how data will be collected to create and refine the AI features...",
        "features_metrics": "Feature Metrics define the key performance indicators (KPIs) and other metrics used to measure and analyze the performance of the AI feature..."
    },
    "acceptance_criteria": {
        "accuracy": "The extent to which the AI model's outputs align with expected results...",
        "performance_latency": "The speed and efficiency of the AI application, minimizing response times...",
        "cost_at_scale": "Scale and cost criteria assess the AI application's ability to handle increased load...",
        "kpis": "Product-specific feature key performance indicators to grade health over time..."
    },
    "challenges_and_considerations": {
        "risks": "Identification and analysis of potential risks...",
        "innovations": "Innovative features and technologies being integrated...",
        "dependencies": "Internal and external dependencies critical to the project...",
        "events": "Key events that could impact the project timeline or scope...",
        "contingency_plans": "Contingency strategies for managing unforeseen issues..."
    },
    "conclusion": {
        "summary": "Including key next steps..."
    }
})


# Function to format the templates with provided variables
def format_template(template, **kwargs):
    return template.format(**kwargs)


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
        await cl.Message(
            content=f"User Proposal: {res['output']}.\n\nStarting...",
        ).send()

        user_proposal = res['output']

        # populate the PRD template
        prd_sys1 = format_template(PRD_PROMPT_TEMPLATE, user_proposal=user_proposal)

        # call the PRD agent
        prd_response = await llm_call(user_prompt=user_proposal, system_prompt=prd_sys1)
        prd_response_raw = prd_response.choices[0].message.content # get PRD from LLM

        # send PRD output to UI
        prd_msg = cl.Message(content=prd_response_raw)
        await prd_msg.send()
        
        # populate the designer template
        designer_prompt = format_template(DESIGNER_PROMPT_TEMPLATE, prd_response_raw=prd_response_raw, prd_json=PRD_JSON_TEMPLATE, user_proposal=user_proposal)
        
        # call the designer agent
        designer_response = await llm_call(designer_prompt)
        designer_output = designer_response.choices[0].message.content
        
        # send designer output to UI
        designer_output_msg = cl.Message(content=designer_output)
        await designer_output_msg.send()

        # update messages
        await prd_msg.update()
        await designer_output_msg.update()


####
# TO DO:
# ⭐⭐⭐⭐⭐ output message as download
# ⭐⭐⭐      have follow up messages revise the original output or give feedback
# ⭐⭐⭐      have starter message for users who don't have an idea yet
####

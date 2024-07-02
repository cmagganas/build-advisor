import chainlit as cl

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="AI-powered financial advisor",
            message="I want to build an AI-powered financial advisor that can provide personalized investment advice based on user input and market data. Start by asking me about my investment goals and risk tolerance.",
            icon="/public/dollar.svg",
        ),
        cl.Starter(
            label="Healthcare chatbot",
            message="Can you help me create a healthcare chatbot that can answer common medical questions and provide guidance based on user symptoms? Start by asking me about the types of questions and symptoms it should handle.",
            icon="/public/heart.svg",
        ),
        cl.Starter(
            label="E-commerce recommendation engine",
            message="I want to develop an e-commerce recommendation engine that suggests products to users based on their browsing and purchase history. Start by asking me about the types of products and data sources we should use.",
            icon="/public/laptop.svg",
        ),
        cl.Starter(
            label="Personalized workout planner",
            message="Help me create a personalized workout planner that generates fitness routines based on user preferences and fitness levels. Start by asking me about my current fitness routine and goals.",
            icon="/public/bicep.svg",
        ),
    ]

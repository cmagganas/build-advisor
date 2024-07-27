import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    await cl.Message(content=f"Echo: {message.content}").send()

    for length in [1000, 2000, 5000, 10000]:
        test_string = 'a\n' * length
        await cl.Message(content=f"String of length {length}: {test_string}").send()

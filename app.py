import os

from openai import AsyncOpenAI
import chainlit as cl

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL"))


settings = {
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}


@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )


@cl.on_message
async def main(message: cl.Message):
    message_history = cl.user_session.get("message_history")
    message_history.append({"role": "user", "content": message.content})

    msg = cl.Message(content="")
    stream = True

    response = await client.chat.completions.create(
        messages=message_history, stream=stream, **settings
    )

    if stream:
        async for part in response:
            if token := part.choices[0].delta.content or "":
                await msg.stream_token(token)
    else:
        await cl.Message(response.choices[0].message.content).send()

    message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()

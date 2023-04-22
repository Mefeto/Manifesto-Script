import openai

openai.api_key = "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"
conversation = []

while True:
    user_input = input("아무거나 써보셈요 : ")
    conversation.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        temperature=0
    )

    print("\n" + response['choices'][0]['message']['content'] + "\n")

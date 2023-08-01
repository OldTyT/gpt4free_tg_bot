import g4f

response = g4f.ChatCompletion.create(model='gpt-4', provider=g4f.Provider.ChatgptAi, messages=[
                                     {"role": "user", "content": "Hello world"}])

for message in response:
    print(message)

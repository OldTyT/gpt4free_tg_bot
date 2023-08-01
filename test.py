import g4f

response = g4f.ChatCompletion.create(model='gpt-4', provider=g4f.Provider.Bing, messages=[
                                     {"role": "user", "content": "Hello world"}], stream=True)

for message in response:
    print(message)

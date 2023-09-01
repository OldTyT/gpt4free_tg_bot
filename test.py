"""Testing g4f provider."""
import g4f

response = g4f.ChatCompletion.create(
    model="gpt-3.5-turbo",
    provider=g4f.Provider.DeepAi,
    messages=[{"role": "user", "content": "Hello world"}],
)

for message in response:
    print(message)  # noqa: T201

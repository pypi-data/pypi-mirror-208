[![PyPI version](https://badge.fury.io/py/freeGPT.svg)](https://badge.fury.io/py/freeGPT)
[![Downloads](https://static.pepy.tech/personalized-badge/freeGPT?period=month&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads)](https://pepy.tech/project/freeGPT)
# freeGPT
A Python package that gives access to GPT3 &amp; GPT4 models for free.
<br>
*Get started by doing: `pip install freeGPT`*
## Examples
#### GPT-3
```python
from freeGPT import gpt3

chat = []

def send_prompt():
    try:
        prompt = input("> ")
        response = gpt3.Completion.create(prompt=prompt, chat=chat)
        print("Response:", response.text)
        chat.append({"question": prompt, "answer": response.text})
    except Exception as e:
        print("Error:", str(e))

while True:
    send_prompt()
```
#### GPT-4
```python
from freeGPT import gpt4

token = gpt4.Account.create(logging=True)
print("Token:", token) 

def send_prompt():
    try:
        prompt = input("> ")
        for response in gpt4.StreamingCompletion.create(token=token, prompt=prompt, model="gpt-4"):
            print("Response:", response.text, end="")
    except Exception as e:
        print("Error:", str(e))

while True:
    send_prompt()
```
## Source
| Models        | Websites                                 |
| ------------- | -----------------------------------------|
| GPT-3         | [you.com](https://you.com)     |
| GPT-4         | [forefront.ai](https://chat.forefront.ai)|
## Conclusion
### TODO-List:
- [x] Add GPT-4
- [ ] Make the library well-documented
- [ ] Make the over-all library easier to use
- [ ] Make the over-all library easier to understand
### Star History
[![Star History Chart](https://api.star-history.com/svg?repos=Ruu3f/freeGPT&type=Date)](https://github.com/Ruu3f/freeGPT/stargazers)
#### Original by [xtekky](https://github.com/xtekky), currently maintained by Ruu3f.
#### Completing the TODO-List when this repository hits 30 stars.

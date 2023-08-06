
# chatglm-llm 


## TODO

[x] llm
[x] async support
[x] websocket API


## if want to deploy chatglm as websocket api server

> # after 
> pip install . -U
> # then 
>  chatglm-web


## examples for use chatglm-llm 

### use local llm

#### Download chatglm-6b (cpu only use this version)
```bash
git lfs clone https://huggingface.co/THUDM/chatglm-6b

cp -a chatglm-6b ~/.cache/chatglm # this is default model_path load .
```

> after downloads chatglm
```python
# default model_path is   ~/.cache/chatglm
from chatglm_src import ChatGLMLLM
llm = ChatGLMLLM.load(verbose=True, cpu=True)
llm("中国的首都在哪里？")

```

### use remote


#### normal version

```python
from chatglm_src import ChatGLMLLM
from langchain.callbacks import StdOutCallbackHandler
from typing import Any, Coroutine

class MyCallbackHandler(StdOutCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs: Any) -> Coroutine[Any, Any, None]:
        print(token, end='', flush=True)

# Async implement ..... (see doc)


remote_ip = "localhost"
llm = ChatGLMLLM(verbose=True, remote_host=remote_ip, callbacks=[MyCallbackHandler()])


```

#### async version

> async must use chains

```python
import asyncio
from chatglm_src import ChatGLMLLM
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


from langchain.callbacks import StdOutCallbackHandler
from typing import Any, Coroutine

class MyCallbackHandler(StdOutCallbackHandler):
    def on_llm_new_token(self, token: str, **kwargs: Any) -> Coroutine[Any, Any, None]:
        print(token, end='', flush=True)


remote_ip = "localhost"
llm = ChatGLMLLM(verbose=True, remote_host=remote_ip, callbacks=[MyCallbackHandler()])
prompt = PromptTemplate(
        input_variables=["prompt"],
        template="{prompt}",
)
chain = LLMChain(llm=llm, prompt=prompt)
await chain.acall("中国的首都在哪里？")
```
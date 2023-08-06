from asyncio import coroutines
from typing import List, Optional
import langchain
from langchain.llms.base import LLM
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import pathlib
import os, json
import asyncio
from termcolor import colored

import datetime
from hashlib import md5
import time
import numpy as np
from aiowebsocket.converses import AioWebSocket
from websocket import create_connection
import websockets
from websockets.server import serve

try:
    from transformers import AutoTokenizer, AutoModel
    from langchain.embeddings import HuggingFaceEmbeddings
    from accelerate import load_checkpoint_and_dispatch
    import torch, gc
    import gptcache
    from gptcache.processor.pre import get_prompt
    from gptcache.manager.factory import get_data_manager
    from langchain.cache import GPTCache
    from langchain.callbacks.manager import BaseCallbackManager, CallbackManagerForLLMRun
    DEFAULT_CACHE_MAP_PATH = str(pathlib.Path.home() / ".cache" / "local_qa_cache_map")
    i = 0

    def init_gptcache_map(cache_obj: gptcache.Cache):
        global i
        cache_path = f'{DEFAULT_CACHE_MAP_PATH}_{i}.txt'
        cache_obj.init(
            pre_embedding_func=get_prompt,
            data_manager=get_data_manager(data_path=cache_path),
        )
        i += 1
    
    langchain.llm_cache = GPTCache(init_gptcache_map)
    print(colored("init gptcache", "green"))
except Exception as e:
    print("use remote ignore this / load transformers failed, please install transformers and accelerate first and torch.")
from .callbacks import AsyncWebsocketHandler, AsyncWebSocksetCallbackManager



## LLM for chatglm
# only load from local's path
# default path is in ~/.cache/chatglm, if not exists, will download from huggingface'url :https://huggingface.co/THUDM/chatglm-6b
# 
"""Common utility functions for working with LLM APIs."""
import re
from typing import List, Dict, Any, Optional, Union
TODAY = datetime.datetime.now()
PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"
# from transformers import AutoModel, AutoTokenizer

os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"
def load_model_on_gpus(checkpoint_path, num_gpus=2):
    # 总共占用13GB显存,28层transformer每层0.39GB左右
    # 第一层 word_embeddings和最后一层 lm_head 层各占用1.2GB左右
    num_trans_layers = 28
    vram_per_layer = 0.39
    average = 13/num_gpus
    used = 1.2
    device_map = {'transformer.word_embeddings': 0,
                  'transformer.final_layernorm': num_gpus-1, 'lm_head': num_gpus-1}
    gpu_target = 0
    for i in range(num_trans_layers):
        if used > average-vram_per_layer/2 and gpu_target < num_gpus:
            gpu_target += 1
            used = 0
        else:
            used += vram_per_layer
        device_map['transformer.layers.%d' % i] = gpu_target

    model = AutoModel.from_pretrained(
        checkpoint_path, trust_remote_code=True)
    model = model.eval()
    model = load_checkpoint_and_dispatch(
        model, checkpoint_path, device_map=device_map, offload_folder="offload", offload_state_dict=True).half()
    return model

def auto_configure_device_map(num_gpus: int) -> Dict[str, int]:
    # transformer.word_embeddings 占用1层
    # transformer.final_layernorm 和 lm_head 占用1层
    # transformer.layers 占用 28 层
    # 总共30层分配到num_gpus张卡上
    num_trans_layers = 28
    per_gpu_layers = 30 / num_gpus

    # bugfix: 在linux中调用torch.embedding传入的weight,input不在同一device上,导致RuntimeError
    # windows下 model.device 会被设置成 transformer.word_embeddings.device
    # linux下 model.device 会被设置成 lm_head.device
    # 在调用chat或者stream_chat时,input_ids会被放到model.device上
    # 如果transformer.word_embeddings.device和model.device不同,则会导致RuntimeError
    # 因此这里将transformer.word_embeddings,transformer.final_layernorm,lm_head都放到第一张卡上
    device_map = {'transformer.word_embeddings': 0,
                  'transformer.final_layernorm': 0, 'lm_head': 0}

    used = 2
    gpu_target = 0
    for i in range(num_trans_layers):
        if used >= per_gpu_layers:
            gpu_target += 1
            used = 0
        assert gpu_target < num_gpus
        device_map[f'transformer.layers.{i}'] = gpu_target
        used += 1

    return device_map


def load_model_on_gpus_old(checkpoint_path, num_gpus: int = 2,device_map = None, **kwargs):
    if num_gpus < 2 and device_map is None:
        model = AutoModel.from_pretrained(checkpoint_path, trust_remote_code=True, **kwargs).half().cuda()
    else:
        from accelerate import dispatch_model
        model = AutoModel.from_pretrained(checkpoint_path, trust_remote_code=True, **kwargs).half()
        if device_map is None:
            device_map = auto_configure_device_map(num_gpus)
        model = dispatch_model(model, device_map=device_map)

    return model

def enforce_stop_tokens(text: str, stop: List[str]) -> str:
    """Cut off the text as soon as any stop words occur."""
    return re.split("|".join(stop), text)[0]

def auto_gc():
    if torch.cuda.is_available():
        # for all cuda device:
        for i in range(0,torch.cuda.device_count()):
            CUDA_DEVICE = f"cuda:{i}"
            with torch.cuda.device(CUDA_DEVICE):
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
    else:
        gc.collect()

class ChatGLMLLM(LLM):
    """
            Load a model from local or remote
        if want to use stream mode:
            'streaming=True'
        if want to use langchain's Callback:
            examples: 'callbacks=[StreamingStdOutCallbackHandler(), AsyncWebsocketHandler()]'

        if want use cpu: # default will try to use gpu
            'cpu=True'
        
        if want to use remote's model:
            'remote_host="xx.xxx.xx.xx"'  , if set this , will auto call by ws://xx.xxx.xxx.xx:15000"
            optional:
                remote_callback: a callback function, will call when receive a new token like  'callback(new_token, history, response)'
                if not set, will print to stdout

    """
    max_token: int = 10000
    temperature: float = 0.01
    top_p = 0.9
    history = []
    history_id = "default"
    tokenizer: Any = None
    model: Any = None
    history_len: int = 10
    model: Any = None
    tokenizer: Any = None
    model_path: str = pathlib.Path.home() / ".cache" / "chatglm"
    cpu: bool = False
    streaming: bool = False
    verbose: bool = False
    callbacks :Any  = [StreamingStdOutCallbackHandler(), AsyncWebsocketHandler()]
    # callback_manager:  Any = BaseCallbackManager
    remote_host: Any = None


    @classmethod
    def load(cls, *args, model_path: str = None, **kargs):
        """
        Load a model from local or remote
        if want to use stream mode:
            'streaming=True'
        if want to use langchain's Callback:
            examples: 'callbacks=[StreamingStdOutCallbackHandler(), AsyncWebsocketHandler()]'

        if want use cpu: # default will try to use gpu
            'cpu=True'
        
        if want to use remote's model:
            'remote_host="xx.xxx.xx.xx"'  , if set this , will auto call by ws://xx.xxx.xxx.xx:15000"
            optional:
                remote_callback: a callback function, will call when receive a new token like  'callback(new_token, history, response)'
                if not set, will print to stdout


        """
        mo = cls(*args, **kargs)
        if "cpu" in kargs and kargs["cpu"]:
            mo.cpu = True
        if model_path is not None:
            mo.model_path = pathlib.Path(model_path)
        # load from local
        if mo.model_path.exists() and mo.remote_host is None:
            if torch.cuda.device_count() > 0:
                print(colored("[GPU]","green"),":",torch.cuda.device_count(), "GPUs" )
                mo.model = load_model_on_gpus_old(mo.model_path, num_gpus=torch.cuda.device_count())
            else:
                mo.model = AutoModel.from_pretrained(mo.model_path, trust_remote_code=True, device_map="auto")
            mo.tokenizer = AutoTokenizer.from_pretrained(mo.model_path, trust_remote_code=True)
        else:
            # load from huggingface
            # use os.system to call git lfs download model
            # then load from local
            # TODO: use git lfs to download model
            pass
        if mo.remote_host is not None:
            return mo
        if mo.cpu:
            mo.model = mo.model.float()
        # else:
        #     mo.model = mo.model.half().cuda()
        mo.model = mo.model.eval()
        return mo
    
    def set_history(self, hist:List[str]):
        self.history = hist
    
    
    @property
    def _llm_type(self) -> str:
        return "ChatGLM"

    async def _acall(self, prompt: str, stop: List[str] = None):
        if self.streaming:
            # print("async ing ", self.callbacks)
            if not "(history_id:" in prompt:
                prompt = f"(history_id:{self.history_id})" + prompt

            if not isinstance(self.callback_manager, AsyncWebSocksetCallbackManager):
                self.callback_manager = AsyncWebSocksetCallbackManager([i for i in self.callbacks if isinstance(i, AsyncWebsocketHandler)])
            current_completion = ""
            # if self.callback_manager.is_async:
            prompt,history_id, history = await self.callback_manager.on_llm_start(
                prompt,
                None,
                verbose=self.verbose
            )
            if history_id is not None and history is not None:
                self.history_id = history_id
                self.history = history
            for response, history in self.model.stream_chat(self.tokenizer, prompt, self.history, max_length=self.max_token, top_p=self.top_p,
                                               temperature=self.temperature):
                
                delta = response[len(current_completion) :]
                current_completion = response
                data = {"response": response, "history": history,"query": prompt, "verbose":self.verbose}
                if self.callback_manager.is_async:
                    # print(".", end="", flush=True)
                    await self.callback_manager.on_llm_new_token(
                        delta, verbose=self.verbose, **data
                    )
                else:
                    # print("+", end="", flush=True)
                    self.callback_manager.on_llm_new_token(
                        delta, verbose=self.verbose, **data
                    )
            auto_gc()
            self.history = self.history+[[prompt, current_completion]]
            await self.callback_manager.on_llm_end(
                {
                    "id": self.history_id,
                    "history": self.history,
                },
                verbose=self.verbose
            )
            return current_completion
        elif self.remote_host is not None :
            uri = f"ws://{self.remote_host}:15000"
            result = ''
            self.callback_manager =  BaseCallbackManager(self.callbacks)
            self.callback_manager.set_handlers(self.callbacks)
            async with AioWebSocket(uri) as aws:
                converse = aws.manipulator
                
                user_id = md5(time.asctime().encode()).hexdigest()
                await converse.send(json.dumps({"user_id":user_id, "password":PASSWORD}).encode())
                res = await converse.receive()
                res = res.decode()
                if res != "ok":
                    raise Exception("password error:"+res)
                data = json.dumps({"prompt":prompt, "history":self.history}).encode()
                await self.asend_to_remote(data, converse)

                self.callback_manager.on_llm_start(prompt, None, verbose=self.verbose)
                while 1:
                    res = await converse.receive()
                    msg = json.loads(res.decode())
                    # { "new":delta,"response": response, "history": history,"query": prompt}
                    if "stop" in msg:
                        break
                    new_token = msg["new"]
                    response = msg["response"]
                    history = msg["history"]
                    self.callback_manager.on_llm_new_token(new_token, response=response, history=history, query=prompt, verbose=self.verbose)
                    result = response
            self.history = self.history+[[prompt, result]]
            self.callback_manager.on_llm_end(result, verbose=self.verbose)
            return result


                
        else:
            response, _ = self.model.chat(
                self.tokenizer,
                prompt,
                history=self.history[-self.history_len:] if self.history_len > 0 else None,
                max_length=self.max_token,
                top_p=self.top_p,
                temperature=self.temperature,
            )
            response = enforce_stop_tokens(response, stop or [])
            self.history = self.history+[[prompt, response]]
            return response

    def send_to_remote(self,data,ws):
        """
        every chunk of data is 2M
        """
        for i in range(0, len(data), 1024*1024*2):
            ws.send(data[i:i+1024*1024*2])
        ws.send("[STOP]")

    async def asend_to_remote(self, data, ws):
        """
        every chunk of data is 2M
        """
        for i in range(0, len(data), 1024*1024*2):
            await ws.send(data[i:i+1024*1024*2])
        await ws.send("[STOP]")
    
    def _call(self, prompt: str, stop: List[str]  = None,run_manager: Optional[CallbackManagerForLLMRun] = None) -> str:
        if self.streaming:
            current_completion = ""
            if self.verbose:
                print("streaming")
            
            for response, history in self.model.stream_chat(self.tokenizer, prompt, self.history, max_length=self.max_token, top_p=self.top_p,
                                               temperature=self.temperature):
                delta = response[len(current_completion) :]
                current_completion = response
                data = {"response": response, "history": history,"query": prompt}
                if self.verbose:
                    print(delta, end='', flush=True)
                self.callback_manager.on_llm_new_token(
                    delta, verbose=self.verbose, **data
                )
            auto_gc()
            self.history = self.history+[[prompt, current_completion]]
            return current_completion
        elif self.remote_host is not None :
            ws = create_connection(f"ws://{self.remote_host}:15000")
            user_id = md5(time.asctime().encode()).hexdigest()
            # self.callback_manager =  langchain.callbacks.base.BaseCallbackManager(self.callbacks)
            
            # self.callback_manager =  BaseCallbackManager(self.callbacks)
            # self.callback_manager.set_handlers(self.callbacks)
            ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
            # time.sleep(0.5)
            res = ws.recv()
            if res != "ok":
                print(colored("[info]:","yellow") ,res)
                raise Exception("password error")
            result = ''
            data = json.dumps({"prompt":prompt, "history":self.history})
            self.send_to_remote(data, ws)
            
            for callback in self.callbacks:
                callback.on_llm_start(
                    None,
                    prompt,
                    run_id=user_id,
                    verbose=self.verbose
                )
            while 1:
                res = ws.recv()
                msg = json.loads(res)
                # { "new":delta,"response": response, "history": history,"query": prompt}
                if "stop" in msg:
                    break
                new_token = msg["new"]
                response = msg["response"]
                history = msg["history"]
                msg["verbose"] = self.verbose
                # self.remote_callback(new_token, history, response)
                
                # self.callback_manager.on_llm_new_token(new_token, **msg)
                for callback in self.callbacks:
                    callback.on_llm_new_token(
                        new_token,
                        **msg
                    )
                result = response
            for callback in self.callbacks:
                callback.on_llm_end(result, verbose=self.verbose)
            
            self.history = self.history+[[prompt, result]]
            return result
        else:
            response, _ = self.model.chat(
                self.tokenizer,
                prompt,
                history=self.history[-self.history_len:] if self.history_len>0 else [],
                max_length=self.max_token,
                temperature=self.temperature,
            )
            auto_gc()
            if stop is not None:
                response = enforce_stop_tokens(response, stop)
            self.history = self.history+[[prompt, response]]
            return response



class WebsocketWrap:
    def __init__(self, llm,embeding, websocket):
        self.websocket = websocket
        self.llm = llm
        self.embeding = embeding
    
    async def reply(self, data):
        await self.websocket.send(str(len(data)))
        for i in range(0,len(data), 1024*1024*2):
            await self.websocket.send(data[i:i+1024*1024*2])
        await self.websocket.send("[STOP]")
    
    async def __call__(self, prompt=None, embed_documents=None,embed_query=None,history=None):
        try:
            # assert prompt is not None 
            if prompt is not None:
                assert isinstance(prompt, str)
                llm = self.llm
                current_completion = ""
                if history is not None and isinstance(history, list):
                    llm.history = history
                for response, history in llm.model.stream_chat(llm.tokenizer, prompt, llm.history, max_length=llm.max_token, top_p=llm.top_p,
                                                    temperature=llm.temperature):
                    delta = response[len(current_completion) :]
                    current_completion = response
                    data = { "new":delta,"response": response, "history": history,"query": prompt}
                    await self.websocket.send(json.dumps(data))
                data = { "new":delta,"response": response, "history": history,"query": prompt, "stop":True}
                
                await self.websocket.send(json.dumps(data))
            elif embed_query is not None:
                res = self.embeding.embed_query(embed_query)
                data = { "embed":res} 
                data = json.dumps(data, cls=NumpyEncoder)
                await self.reply(data)
            elif embed_documents is not None:
                res = self.embeding.embed_documents(embed_documents)
                data = { "embed":res}
                data = json.dumps(data, cls=NumpyEncoder)
                await self.reply(data)
        finally:
            auto_gc()



class AsyncServer:
    __users = {}
    _callbacks = {"hello": lambda x: colored("[hello]","green") + time.asctime()}
    llm = None
    embeding = None
    @classmethod
    async def echo(cls,websocket):
        try:
            print(colored("[connected]","green"),":",websocket)
            no = 0
            messages = ""
            async for message in websocket:
                print(colored("[recv]","yellow") ,":",message)
                if no == 0:
                    if await cls.user(message, websocket):
                        no += 1
                        continue
                    else:
                        await websocket.close()
                        break
                if message.endswith("[STOP]"):
                    messages += message[:-6]
                    break
                else:
                    messages += message
                no += 1
            if len(messages) < 1000:
                print(colored("[recv]","green") ,":",messages)
            else:
                print(colored("[recv]","green") ,":",messages[:10]+ f"...{len(messages)}...{messages[-10:]}")
            if len(messages) == 0:
                await cls.del_user(websocket)
                return
            oneChat = WebsocketWrap(cls.llm,cls.embeding, websocket)
            await oneChat(**json.loads(messages))
                


        except websockets.exceptions.ConnectionClosedOK:
            print(colored("[closed]","yellow"),":",websocket)
            await cls.del_user(websocket)
        except websockets.exceptions.ConnectionClosedError:
            print(colored("[closed]","red"),":",websocket)
            await cls.del_user(websocket)

        except Exception as e:
            
            print(colored("[error]","red"),":",e)
            raise e
    
    @classmethod
    def add_callback(cls, name, callback):
        cls._callbacks[name] = callback

    @classmethod
    async def call(cls, message, websocket):
        try:
            msgs = json.loads(message)
            if "user_id" not in msgs :
                await websocket.send("error")
                await websocket.close()
                await cls.del_user(websocket)
                return
            user_id = msgs["user_id"]
            if user_id not in cls.__users.values():
                await websocket.send("not login")
                await websocket.close()
                await cls.del_user(websocket)
                return
            if "callback" in msgs:
                callback = cls._callbacks[msgs["callback"]]
                args = msgs.get("args",[])
                kwargs = msgs.get("kwargs",{})

                res = await callback(*args, **kwargs)
                await websocket.send(json.dumps({
                    "result":res,
                    "user_id":user_id,
                    "callback":msgs["callback"],
                }))
            
        except Exception as e:
            print(colored("[error]","red"),":",e)
            await websocket.close()
            await cls.del_user(websocket)

    @classmethod
    async def main(cls, port):
        async with serve(cls.echo, "0.0.0.0", port):
            await asyncio.Future()  # run forever
    
    @classmethod
    async def user(cls, first_msg, websocket) -> bool:
        try:
            d = json.loads(first_msg)
            user_id = d["user_id"]
            password = d["password"]
            if password != PASSWORD:
                return False
            print(colored("[user-login]","green"),":",user_id)
            cls.__users[websocket] =  user_id
            await websocket.send("ok")
            return True
        except Exception as e:
            print(colored("[error]","red"),":",websocket, e)
    
    @classmethod
    async def del_user(cls,websocket):
        if websocket in cls.__users:
            del cls.__users[websocket]

    @classmethod
    def start(cls,port=15000, model_path=None):
        cpu = False
        if not torch.cuda.is_available():
            cpu = True
        print(colored(f"[cpu:{cpu} ]","green"),":",f"listen:0.0.0.0:{port}")
        cls.embeding = HuggingFaceEmbeddings(model_name="GanymedeNil/text2vec-large-chinese")
        print(colored(f"[embedding: use cpu{cpu} ]","green"),":",f"GanymedeNil/text2vec-large-chinese")
        cls.llm = ChatGLMLLM.load(model_path=model_path, cpu=cpu, streaming=True)
        print(colored(f"[ starting ]","green"),":",f"listen:0.0.0.0:{port}")
        asyncio.run(cls.main(port))


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
    
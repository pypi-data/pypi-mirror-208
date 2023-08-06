from typing import List
from langchain.embeddings.base import Embeddings
from langchain.embeddings import HuggingFaceEmbeddings
from websocket import create_connection
from hashlib import md5
import time
import json
import tqdm
import datetime
from typing import List, Dict, Any, Optional, Union
from termcolor import colored

TODAY = datetime.datetime.now()
PASSWORD = "ADSFADSGADSHDAFHDSG@#%!@#T%DSAGADSHDFAGSY@#%@!#^%@#$Y^#$TYDGVDFSGDS!@$!@$" + f"{TODAY.year}-{TODAY.month}"

class ChatGLMEmbeding(Embeddings):

    remote_host :str = None

    def __init__(self, model_path: str=None, remote_host:str=None):
        if remote_host is None:
            self._emb = HuggingFaceEmbeddings(model_name=model_path)
        else:
            self.remote_host = remote_host

    def send_and_recv(self, data, ws):
        try:
            for i in tqdm.tqdm(range(0, len(data), 1024*102), desc="sending data"):
                ws.send(data[i:i+1024*102])
            ws.send("[STOP]")
            message = ""
            total = int(ws.recv())
            bar = tqdm.tqdm(desc="receiving data", total=total)
            while 1:
                res = ws.recv()
                message += res
                bar.update(len(res))
                if message.endswith("[STOP]"):
                    message = message[:-6]
                    break
            msg = json.loads(message)
            return msg
        except Exception as e:
            raise e

    def embed_documents_remote(self, texts):
        ws = create_connection(f"ws://{self.remote_host}:15000")
        user_id = md5(time.asctime().encode()).hexdigest()
        ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
        # time.sleep(0.5)
        res = ws.recv()
        if res != "ok":
            print(colored("[info]:","yellow") ,res)
            raise Exception("password error")
        
        data = json.dumps({"embed_documents":texts})
        try:
            msg = self.send_and_recv(data, ws)
            return msg["embed"]
        except Exception as e:
            print(e)
            import ipdb;ipdb.set_trace()
    
    def embed_query_remote(self, text):
        ws = create_connection(f"ws://{self.remote_host}:15000")
        user_id = md5(time.asctime().encode()).hexdigest()
        ws.send(json.dumps({"user_id":user_id, "password":PASSWORD}))
        # time.sleep(0.5)
        res = ws.recv()
        if res != "ok":
            print(colored("[info]:","yellow") ,res)
            raise Exception("password error")
        
        data = json.dumps({"embed_query":text})
        msg = self.send_and_recv(data, ws)
        return msg["embed"]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.remote_host is not None:
            return self.embed_documents_remote(texts)
        return self._emb.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        if self.remote_host is not None:
            return self.embed_query_remote(text)
        return self._emb.embed_query(text)
import os
import langchain
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

from contextlib import contextmanager
import gptcache
from gptcache.processor.pre import get_prompt
from gptcache.manager.factory import get_data_manager
from langchain.cache import GPTCache
from termcolor import colored
import pathlib

DEFAULT_EMBEDDING_PATH = str(pathlib.Path.home() / ".cache" / "chatglm-embedding" / "base-embedding")

DEFAULT_LOCAL_QA_VS_PATH = str(pathlib.Path.home() / ".cache" / "local_qa_vs")
DEFAULT_CACHE_MAP_PATH = str(pathlib.Path.home() / ".cache" / "local_qa_cache_map")
if not os.path.exists(DEFAULT_LOCAL_QA_VS_PATH):
    os.makedirs(DEFAULT_LOCAL_QA_VS_PATH)

i = 0
# file_prefix = "data_map"
def load_embedding(model_path=DEFAULT_EMBEDDING_PATH):
    try:
        print(colored("Loading embeddings...", "green"))
        return HuggingFaceEmbeddings(model_name=model_path)
    finally:
        print(colored("Embeddings loaded.", "green"))

def init_gptcache_map(cache_obj: gptcache.Cache):
    global i
    cache_path = f'{DEFAULT_CACHE_MAP_PATH}_{i}.txt'
    cache_obj.init(
        pre_embedding_func=get_prompt,
        data_manager=get_data_manager(data_path=cache_path),
    )
    i += 1

langchain.llm_cache = GPTCache(init_gptcache_map)


class KnowdageQA:
        
    @classmethod
    def create_from_local(cls,kn_name ,docs, embeddings, vs_path=DEFAULT_LOCAL_QA_VS_PATH):
        vs_path = pathlib.Path(vs_path) / kn_name
        print("kn name:", kn_name)
        cls.save_loaders(docs, embeddings=embeddings,vs_path=vs_path)


    def __init__(self,llm,embeddings=None, vs_path=DEFAULT_LOCAL_QA_VS_PATH, max_history_len=10, top_k=5):
        self.embeddings = embeddings
        if self.embeddings is  None:
            self.embeddings = load_embedding(model_path=DEFAULT_EMBEDDING_PATH)

        self.db = None
        self.vs_path_dir = vs_path
        self.llm = llm
        self.top_k = top_k
        self.max_history_len = max_history_len
        self.history = self.llm.history

    def load(self, name):
        self.db = FAISS.load_local( str(pathlib.Path(self.vs_path_dir)/name), self.embeddings)

    @classmethod
    def save_loaders(cls,docs, embeddings=None, vs_path=DEFAULT_LOCAL_QA_VS_PATH, model_path=DEFAULT_EMBEDDING_PATH):
        if embeddings is None:
            embeddings = load_embedding(model_path=model_path)

        if os.path.isdir(vs_path) and os.path.exists(str(pathlib.Path(vs_path) / "index.faiss")):
            db = FAISS.load_local(vs_path, embeddings)
            db.add_documents(docs)
        else:
            db = FAISS.from_documents(docs, embeddings)
        db.save_local(vs_path)
        return db

    @contextmanager
    def with_context(self, history):
        try:
            old_history = self.history
            self.history = history
            yield
        finally:
            self.history = old_history

    def __call__(self, query):
        assert self.db is not None
        prompt_template = """基于以下已知信息，简洁和专业的来回答用户的问题。
        如果无法从中得到答案，请说 "根据已知信息无法回答该问题" 或 "没有提供足够的相关信息"，不允许在答案中添加编造成分。
        
        已知内容:
        {context}
        
        问题:
        {question}"""
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        if len(self.history) > self.max_history_len:
            self.history = self.history[-self.max_history_len:]
        self.llm.history = self.history
        # vector_store = FAISS.load_local(vs_path, self.embeddings)
        knowledge_chain = RetrievalQA.from_llm(
            llm=self.llm,
            retriever=self.db.as_retriever(search_kwargs={"k": self.top_k}),
            prompt=prompt
        )
        knowledge_chain.combine_documents_chain.document_prompt = PromptTemplate(
            input_variables=["page_content"], template="{page_content}"
        )

        knowledge_chain.return_source_documents = True
        result = knowledge_chain({"query": query})
        self.llm.history[-1][0] = query
        self.history = self.llm.history
        return result, self.llm.history
    
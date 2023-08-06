
from setuptools import setup, find_packages


setup(name='chatglm-llm',
    version='1.3.3',
    description='chatglm llm',
    url='https://github.com/xxx',
    author='auth',
    author_email='xxx@gmail.com',
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    extras_require={
        "all": [
            'sentence_transformers',
            'tensorboard',
            "protobuf",
            "cpm_kernels",
            "mdtex2html",
            "sentencepiece",
            "accelerate",
            'torch',    
            'transformers',
        ],
    },
    install_requires=[
        'requests',
        'termcolor',
        'tqdm',
        'gptcache',
        'numpy',
        'pypdf',
        'langchain',
        'websockets',
        'websocket-client',
        'unstructured',
        'aiowebsocket',
        ],
    entry_points={
        'console_scripts': [
            'chatglm-web=chatglm_src.cmd:main',
        ]
    },

)

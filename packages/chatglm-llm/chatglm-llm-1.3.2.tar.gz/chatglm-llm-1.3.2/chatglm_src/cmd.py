from .llm import AsyncServer
import argparse
import pathlib

parser = argparse.ArgumentParser(description='Start a chatglm server.')
parser.add_argument('--port', type=int, default=15000, help='port number')
parser.add_argument("--model-path", default=str(pathlib.Path.home() / ".cache" / "chatglm"), help="path to model directory")


def main():
    args = parser.parse_args()
    AsyncServer.start(port=args.port, model_path=args.model_path)
from langchain.callbacks.base import BaseCallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    HumanMessage,
    AIMessage
)
from dotenv import load_dotenv
from flask import Flask
from rich.console import Console
from rich.markdown import Markdown
import os
import sys
import argparse
from .prompts import mentor_prompt, architect_prompt


load_dotenv()
api_key = os.environ['OPENAI_API_KEY']
app = Flask(__name__)
console = Console()

def write_with_code_block(text):
    start_code_block = '\033[1;37;40m'
    end_code_block = '\033[0m'
    sys.stdout.write(start_code_block + text + end_code_block)
    sys.stdout.flush()


class CustomStreamingStdOutCallbackHandler(StreamingStdOutCallbackHandler):
    def on_llm_new_token(self, token, **kwargs):
        pass

class CustomChatOpenAI(ChatOpenAI):
    def __call__(self, messages, callback=None, stop=None):
        result = super().__call__(messages, stop=stop)

        if callback:
            callback(result)

        return result
    
    
def call_gpt(code, prompt):
    print(prompt)
    chat = CustomChatOpenAI(streaming=True, model_name="gpt-3.5-turbo", callback_manager=BaseCallbackManager([StreamingStdOutCallbackHandler()]), verbose=True)
    chat([HumanMessage(content=prompt)])


def get_file_content(file_names):
    content = ""
    for file in file_names:
        with open(file, 'r') as f:
            content += f"### {os.path.basename(file)}\n\n\n" + f.read() + "\n"
    return content



def main(args=None):
    print('app started')
    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('mode', metavar='M', type=str, choices=['mentor', 'architect'],
                        help='Mode of operation: mentor or architect')
    parser.add_argument('file_names', metavar='N', type=str, nargs='+',
                        help='Files to process')

    args = parser.parse_args(args)
    while True:
        file_content = get_file_content(args.file_names)
        if args.mode == 'mentor':
            call_gpt(file_content, mentor_prompt(file_content))
        elif args.mode == 'architect':
            call_gpt(file_content, architect_prompt(file_content))
        input("Press Enter to continue...")


if __name__ == '__main__':
    main()

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

load_dotenv()
api_key = os.environ['OPENAI_API_KEY']
app = Flask(__name__)
console = Console()

def write_with_code_block(text):
    start_code_block = '\033[1;37;40m'  # White text with black background
    end_code_block = '\033[0m'  # Reset to default colors
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
    
    
def call_gpt(code):
    print(code)
    chat = CustomChatOpenAI(streaming=True, model_name="gpt-3.5-turbo", callback_manager=BaseCallbackManager([StreamingStdOutCallbackHandler()]), verbose=True)
    chat([HumanMessage(content=f"""The following code may have a bug. If it exists, tell me exactly where to look. In your response only tell me concisely exactly where to look. Be as concise as possible. Respond like, You may want to look at _____ where there's an issue with ____ and you can fix it by _____. Be specific with your suggested fix. Show a minimal representation of the fixed code.
                                              
    If there is no obvious bug simply reply, "no bug".
    
    Next you'll play the role of a software architect. You'll take a second look at our architecture decisions and recommend alternatives if there's something better.
    
    If there is no obvious recommendation, simply reply, "no rec"
    
    Below I will paste the contents from a bunch of my files. If I show you errors pay special attention to the errors and help me fix them.
{code}""")])


def get_file_content(file_names):
    content = ""
    for file in file_names:
        with open(file, 'r') as f:
            content += f"### {os.path.basename(file)}\n\n\n" + f.read() + "\n"
    return content



def main(args=None):
    print('app started')
    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('file_names', metavar='N', type=str, nargs='+',
                        help='Files to process')

    args = parser.parse_args(args)
    while True:
        file_content = get_file_content(args.file_names)
        call_gpt(file_content)
        input("Press Enter to continue...")


if __name__ == '__main__':
    main()

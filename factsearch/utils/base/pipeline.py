import yaml
from factsearch.utils.openai_wrapper import OpenAIChat
from factsearch.utils.ollama_wrapper import OllamaChat
import os
import pathlib

class pipeline():
    def __init__(self, domain, foundation_model):
        if 'gpt' in foundation_model:
            self.company = 'openai'
            self.chat = OpenAIChat(model_name=foundation_model)
        else:
            self.company = 'ollama'
            self.chat = OllamaChat(model_name=foundation_model)

        self.prompts_path = os.path.join(os.path.dirname(pathlib.Path(__file__)), "../prompts/")
        
        with open(os.path.join(self.prompts_path, "self_check.yaml"), 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
        self.self_check_prompt = data[domain]
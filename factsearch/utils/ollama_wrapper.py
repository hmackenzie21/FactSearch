import asyncio
import aiohttp
import ast
import os
from typing import List


class OllamaChat():
    def __init__(
        self,
        model_name='qwen3:8b',
        max_tokens=2500,
        temperature=1,
        request_timeout=120,
    ):
        self.config = {
            'model_name': model_name,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'request_timeout': request_timeout,
            'base_url': 'http://localhost:11434/api/chat'
        }

    def _boolean_fix(self, output):
        """Convert JSON boolean strings to Python booleans"""
        return output.replace("true", "True").replace("false", "False")
    
    def _strip_thinking(self, output: str) -> str:
        import re 
        return re.sub(r'<think>.*?</think>', '', output, flags=re.DOTALL).strip()

    def _type_check(self, output, expected_type):
        try:
            output_eval = ast.literal_eval(output)
            if not isinstance(output_eval, expected_type):
                return None
            return output_eval
        except:
            # Fallback: try to extract just the list/dict portion
            try:
                if expected_type == list:
                    start, end = output.find('['), output.rfind(']')
                else:
                    start, end = output.find('{'), output.rfind('}')
                if start != -1 and end != -1 and start < end:
                    output_eval = ast.literal_eval(output[start:end+1])
                    if isinstance(output_eval, expected_type):
                        return output_eval
            except:
                pass
            return None

    async def _single_request(self, messages, retry=3):
        """Make a single request to Ollama API with retry logic"""
        modified_messages = []
        for msg in messages:
            if msg['role'] == 'system':
                modified_messages.append({
                    'role': 'system',
                    'content': msg['content'] + '\n/no_think'
                })
            else:
                modified_messages.append(msg)
        payload = {
            'model': self.config['model_name'],
            'messages': messages,
            'stream': False,
            'options': {
                'temperature': self.config['temperature'],
                'num_predict': self.config['max_tokens']
            }
        }
        
        for attempt in range(retry):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        self.config['base_url'],
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=self.config['request_timeout'])
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data['message']['content']
                        else:
                            print(f'Ollama request failed with status {response.status}')
                            if attempt < retry - 1:
                                await asyncio.sleep(1)
            except asyncio.TimeoutError:
                print(f'Ollama timeout error (attempt {attempt + 1}/{retry}), waiting...')
                if attempt < retry - 1:
                    await asyncio.sleep(1)
            except Exception as e:
                print(f'Ollama request error (attempt {attempt + 1}/{retry}): {e}')
                if attempt < retry - 1:
                    await asyncio.sleep(1)
        
        return None

    async def dispatch_ollama_requests(self, messages_list):
        """Dispatch multiple requests to Ollama in parallel"""
        tasks = [self._single_request(messages) for messages in messages_list]
        return await asyncio.gather(*tasks)

    async def async_run(self, messages_list, expected_type):
        """
        Main entry point matching OpenAIChat interface.
        
        Args:
            messages_list: List of message lists to send to Ollama
            expected_type: Expected return type (list or dict)
            
        Returns:
            List of parsed responses matching expected_type
        """
        retry = 1
        responses = [None for _ in range(len(messages_list))]
        messages_list_cur_index = [i for i in range(len(messages_list))]

        while retry > 0 and len(messages_list_cur_index) > 0:
            print(f'{retry} retry left...')
            messages_list_cur = [messages_list[i] for i in messages_list_cur_index]
            
            predictions = await self.dispatch_ollama_requests(
                messages_list=messages_list_cur,
            )

            preds = [
                self._type_check(self._boolean_fix(self._strip_thinking(prediction)), expected_type) 
                if prediction is not None else None 
                for prediction in predictions
            ]

            finished_index = []
            for i, pred in enumerate(preds):
                if pred is not None:
                    responses[messages_list_cur_index[i]] = pred
                    finished_index.append(messages_list_cur_index[i])
            
            messages_list_cur_index = [
                i for i in messages_list_cur_index 
                if i not in finished_index
            ]
            
            retry -= 1
        
        return responses


# For testing
if __name__ == "__main__":
    async def test_ollama():
        chat = OllamaChat(model_name='qwen3:8b')
        
        # Test list output
        messages_list = [
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Return a JSON list with two items: ['apple', 'banana']. Only return the JSON, nothing else."}
            ]
        ]
        
        results = await chat.async_run(messages_list, list)
        print(f"Test results: {results}")
    
    asyncio.run(test_ollama())
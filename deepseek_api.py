import aiohttp
import json
from typing import List, Dict

class DeepSeekAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
    
    async def chat_complete(self, messages: List[Dict[str, str]]):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    
                    if response.status != 200:
                        error = await response.text()
                        raise Exception(f"API error {response.status}: {error}")
                    
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                    
        except aiohttp.ClientError as e:
            raise Exception(f"Network error: {str(e)}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid API response: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error: {str(e)}")
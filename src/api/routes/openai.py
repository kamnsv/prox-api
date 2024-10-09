from fastapi import APIRouter, HTTPException
from fastapi import Query, UploadFile
from typing import Optional
import base64
import requests

from ..api import API

class OpenAI(API):
    
    def set_routes(self, api: APIRouter):
        @api.post('')
        async def prompt(api_key: str,
                         context: Optional[str]=None,
                         image: UploadFile=None,
                         max_tokens: int=Query(3_000, ge=1, lt=16_384), 
                         model:str=Query('gpt-4o', enum=['gpt-4o', 'gpt-4o-mini', 'gpt-o1']),
                         ) -> str:
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
           
            content = []

            if context:
                content.append({
                    "type": "text",
                    "text": context
                })

            if image:
                image_data = await image.read()
                image_decode = base64.b64encode(image_data).decode('utf-8')
                content.append({
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image_decode}"
                })

            if not len(content):
                raise HTTPException(status_code=400, detail="If you need content to work, please enter context or upload an image")
            
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ],
                "max_tokens": max_tokens
            }

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            result = response.text
            return result
from app.model.ttt import TTT

from agents import function_tool

from typing import List
from pydantic import BaseModel

ttt = TTT()

class Message(BaseModel):
    role: str
    content: str

extract_recommendation_json = {
            "type": "function",
            "name": "extract_recommendation",
            "description": "Назови 2-3 компетенции по методике STAR из стенограммы собеседования, которым соответствует кандидат. Подведи итог, рекомендуешь ли кандидата к найму. Не выдумывайте ничего, используйте только предоставленную стенограмму собеседования. Если не знаешь, то напиши не знаю",
            "parameters": {
                "type": "object",
                "properties": {
                    "Recommendation": {"type": "string", "description": "Извлеченные компетенции из собеседования и рекоментация. Если действия не указаны, не выдумывайте их, просто укажите, что действия не описаны."}
                },
                "required": ["Recommendation"],
                "additionalProperties": False
            },
            "strict": True,
        }

@function_tool
def extract_recommendation(messages: List[Message]) -> str:
    """
    Назови 2-3 компетенции по методике STAR из стенограммы собеседования, которым соответствует кандидат. Подведи итог, рекомендуешь ли кандидата к найму.  Не выдумывайте ничего, используйте только предоставленную стенограмму собеседования.

    Args:
        messages (list): Список сообщений из стенограммы собеседования. Каждое сообщение - словарь, содержащий 'role' и 'content'.

    Return:
        str: Извлечение компетенций по методике STAR из стенограммы собеседования, которым соответствует кандидат. Подведи итог, рекомендуешь ли к найму.
    """

    response = ttt.generate_response_with_function(
        messages=messages,
        functions=[extract_recommendation_json]
    )
    print("Response from extract_action:", response)
    return response
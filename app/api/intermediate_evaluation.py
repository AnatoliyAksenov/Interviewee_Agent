from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import JSONResponse

from app.model.ttt import TTT
from app.model.stt import STT
from app.model.tts import TTS
from openai import OpenAI
from agents import set_default_openai_key, Agent, Runner

import json
import asyncio
import os
from dotenv import load_dotenv
from app.agents.prompts.utils import load_prompts

load_dotenv()

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ttt = TTT()
stt = STT()
tts = TTS()

situation_agent = Agent(
    name="situation_skill_agent",
    instructions="Ты оцениваешь сообщение от пользователя по методике для оценки кандидатов STAR. \
    Ты должен сказать есть ли элемент situation в сообщении. Если он есть, уточни насколько ярко он выражен",
)

task_agent = Agent(
    name="task_skill_agent",
    instructions="Ты оцениваешь сообщение от пользователя по методике для оценки кандидатов STAR. \
    Ты должен сказать есть ли элемент task в сообщении. Если он есть, уточни насколько ярко он выражен",
)

action_agent = Agent(
    name="action_skill_agent",
    instructions="Ты оцениваешь сообщение от пользователя по методике для оценки кандидатов STAR. \
    Ты должен сказать есть ли элемент action в сообщении. Если он есть, уточни насколько ярко он выражен",
)

result_agent = Agent(
    name="result_skill_agent",
    instructions="Ты оцениваешь сообщение от пользователя по методике для оценки кандидатов STAR. \
    Ты должен сказать есть ли элемент result в сообщении. Если он есть, уточни насколько ярко он выражен",
)



# Вебсокет-эндпоинт для интервью
@router.websocket("/ws/intermediate_interview")
async def websocket_interview(ws: WebSocket, persona: str = Query("Junior Python Developer"), skill: str = Query("Python programming")):
    await ws.accept()  # Принимаем подключение

    try:
        while True:
            data = await ws.receive_text()  # сообщение от клиента
            json_data = json.loads(data)

            intermediate_evaluation_prompts = load_prompts("intermediate_evaluation_prompt.yaml").get("intermediate_evaluation_prompt", "")

            agent = Agent(
                name="intermediate_agent",
                instructions=intermediate_evaluation_prompts.format(persona=persona, skill=skill),
                tools=[
                    situation_agent.as_tool(
                        tool_name="get_situation",
                        tool_description="Get Situation from STAR methodology",
                    ),
                    task_agent.as_tool(
                        tool_name="get_task",
                        tool_description="Get Task from STAR methodolog",
                    ),
                    action_agent.as_tool(
                        tool_name="get_action",
                        tool_description="Get Action from STAR methodolog",
                    ),
                    result_agent.as_tool(
                        tool_name="get_result",
                        tool_description="Get Result from STAR methodolog",
                    ),
                ],
            )

            user_input = json_data.get("message", "")
            # Формируем историю сообщений для передачи агенту
            messages = [ttt.create_chat_message(msg["role"], msg["content"]) for msg in json_data.get("history", [])]
            messages.append(ttt.create_chat_message("user", user_input))  # Добавляем текущее сообщение пользователя
            # Получаем ответ от агента
            response = await Runner.run(agent, messages)
            # response = await Runner.run(agent, user_input, context={"messages": messages}) # Вариант с контекстом
            agent_text = response.final_output  # Текстовый ответ агента

            await ws.send_json({"type": "text", "content": agent_text})
    except WebSocketDisconnect:
        pass
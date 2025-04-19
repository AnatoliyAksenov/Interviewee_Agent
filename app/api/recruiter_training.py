from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Request
import base64
import json
import os
import random
from datetime import datetime
from openai import AsyncOpenAI

from app.model.ttt import TTT
from app.model.stt import STT
from app.model.tts import TTS
from app.agents.prompts.utils import load_prompts
from agents import Runner
from app.agents.interviewee_agent import create_interviewee_agent

# Используем директорию /tmp для временных файлов
TEMP_DIR = "/tmp/ai-interview-temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Директория для сохранения логов бесед
LOGS_DIR = "interview_logs"
os.makedirs(LOGS_DIR, exist_ok=True)

router = APIRouter()

ttt = TTT()
stt = STT()
tts = TTS()

# Загружаем промпты для тренировки рекрутера
recruiter_prompts = load_prompts("recruiter_training_prompt.yaml")

# Список доступных профилей личности
PERSONALITY_PROFILES = [
    "stable_leader",
    "reliable_executor", 
    "analytical_strategist",
    "creative_individualist",
    "introverted_empath",
    "assertive_extrovert",
    "melancholic_idealist",
    "anxious_conformist",
    "depressive_realist",
    "suppressed_observer"
]

@router.websocket("/ws/recruiter-training")
async def websocket_recruiter_training(
    ws: WebSocket,
    position: str = Query(...),
    personality: str = Query(...),
    experience: str = Query(...),
    honesty: str = Query(...)
):
    await ws.accept()
    
    # Случайно выбираем профиль личности
    selected_profile = random.choice(PERSONALITY_PROFILES)
    profile_description = recruiter_prompts[selected_profile]

    # Формируем системный промпт на основе выбранных параметров
    system_prompt = recruiter_prompts["recruiter_training_prompt"]
    system_prompt = system_prompt.format(
        position=position,
        persona=profile_description,
        experience=experience,
        honesty=honesty
    )

    # Создаем агента-кандидата
    agent = create_interviewee_agent(system_prompt)

    # Инициализируем историю беседы
    conversation_history = {
        "timestamp": datetime.utcnow().isoformat(),
        "position": position,
        "personality": personality,
        "experience": experience,
        "honesty": honesty,
        "random_profile": {
            "type": selected_profile,
            "description": profile_description
        },
        "messages": []
    }

    try:
        while True:
            data = await ws.receive_text()
            json_data = json.loads(data)

            if json_data["type"] == "end_session":
                # Проводим психологическую оценку перед завершением
                assessment_prompt = """Тебе будет предложен список утверждений. На каждое утверждение нужно дать один из следующих ответов:
- Сильнее всего (5 баллов)
- Очень сильно (4 балла)
- Сильно (3 балла)
- В средней степени (2 балла)
- Меньше всего (1 балл)

ВАЖНО:
1. Отвечай строго в контексте своего профиля и предыдущей беседы
2. Сохраняй последовательность и логику ответов
3. Учитывай свой уровень опыта и тип личности
4. Будь честен в соответствии с заданным уровнем честности
5. Формат ответа должен быть строго таким:
   {
     "statement": "текст утверждения",
     "score": число от 1 до 5,
     "answer": "один из пяти вариантов ответа",
     "explanation": "краткое объяснение почему выбран этот ответ"
   }"""

                # Список утверждений для оценки
                statements = [
                    "Задумываюсь о том, каким будет мое будущее",
                    "Осознаю, что сегодняшний выбор определяет мое будущее",
                    "Готовлюсь к будущему",
                    "Понимаю, какие решения я должен принять в области образовательного и профессионального выбора",
                    "Планирую, как достичь свои цели",
                    "Задумываюсь о своей карьере",
                    "Стараюсь не унывать",
                    "Принимаю решения самостоятельно",
                    "Беру на себя ответственность за свои действия",
                    "Отстаиваю свои убеждения",
                    "Рассчитываю на себя",
                    "Делаю то, что мне по душе",
                    "Исследую мое окружение",
                    "Ищу возможности для личностного роста",
                    "Изучаю варианты, прежде чем сделать выбор",
                    "Рассматриваю различные способы выполнения той или иной работы",
                    "Глубоко вникаю в суть вопросов, которые у меня возникают",
                    "Интересуюсь новыми возможностями",
                    "Эффективно выполняю задачи",
                    "Стараюсь делать все хорошо",
                    "Приобретаю новые навыки",
                    "Работаю в меру своих способностей",
                    "Преодолеваю препятствия",
                    "Решаю проблемы"
                ]

                # Получаем ответы на все утверждения
                assessment_results = []
                for statement in statements:
                    # Добавляем инструкции и утверждение в историю
                    messages = [
                        ttt.create_chat_message("system", assessment_prompt),
                        ttt.create_chat_message("user", f"Оцени следующее утверждение: {statement}")
                    ]
                    
                    # Получаем ответ от агента
                    response = await Runner.run(agent, messages)
                    try:
                        response_data = json.loads(response.final_output)
                        assessment_results.append(response_data)
                    except json.JSONDecodeError:
                        assessment_results.append({
                            "statement": statement,
                            "score": 0,
                            "answer": "Ошибка обработки",
                            "explanation": "Не удалось получить корректный ответ"
                        })
                    
                    # Отправляем прогресс клиенту
                    progress = int((len(assessment_results) / len(statements)) * 100)
                    await ws.send_json({
                        "type": "assessment_progress",
                        "progress": progress,
                        "current_statement": statement
                    })

                # Сохраняем лог беседы и результаты оценки
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{LOGS_DIR}/recruiter_training_{timestamp}.json"
                
                # Формируем финальный лог
                final_log = {
                    "timestamp": conversation_history["timestamp"],
                    "position": position,
                    "personality": personality,
                    "experience": experience,
                    "honesty": honesty,
                    "random_profile": {
                        "type": selected_profile,
                        "description": profile_description
                    },
                    "messages": conversation_history["messages"],
                    "psychological_assessment": assessment_results
                }
                
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(final_log, f, ensure_ascii=False, indent=2)

                # Отправляем результаты оценки клиенту
                await ws.send_json({
                    "type": "assessment_complete",
                    "results": assessment_results
                })
                    
                await ws.close(code=1000)
                return

            elif json_data["type"] == "text":
                user_input = json_data.get("content", "")
                is_audio = False
            elif json_data["type"] == "voice":
                audio_bytes = base64.b64decode(json_data["audio"])
                temp_audio_path = os.path.join(TEMP_DIR, "temp_audio.wav")
                with open(temp_audio_path, "wb") as f:
                    f.write(audio_bytes)
                user_input = stt.transcribe_from_path(temp_audio_path)
                is_audio = True

            # Добавляем сообщение рекрутера в историю
            conversation_history["messages"].append({
                "role": "user",
                "content": user_input
            })

            # Получаем ответ от агента
            messages = [ttt.create_chat_message(msg["role"], msg["content"]) for msg in conversation_history["messages"]]
            response = await Runner.run(agent, messages)
            agent_text = response.final_output

            # Добавляем ответ в историю
            conversation_history["messages"].append({
                "role": "assistant",
                "content": agent_text
            })

            if is_audio:
                # Используем тон голоса из промптов
                voice_tone = recruiter_prompts["recruiter_voice_tone_prompt"]
                tts_response = tts.generate_speech(agent_text, tone=voice_tone)
                agent_audio = base64.b64encode(tts_response.content).decode('utf-8')
                await ws.send_json({
                    "type": "voice",
                    "content": agent_text,
                    "user_text": user_input,
                    "audio": agent_audio,
                    "timestamp": conversation_history["timestamp"],
                    "position": position,
                    "personality": personality,
                    "experience": experience,
                    "honesty": honesty,
                    "random_profile": conversation_history["random_profile"],
                    "messages": conversation_history["messages"]
                })
            else:
                await ws.send_json({
                    "type": "text",
                    "content": agent_text,
                    "timestamp": conversation_history["timestamp"],
                    "position": position,
                    "personality": personality,
                    "experience": experience,
                    "honesty": honesty,
                    "random_profile": conversation_history["random_profile"],
                    "messages": conversation_history["messages"]
                })

    except WebSocketDisconnect:
        # При неожиданном разрыве соединения тоже сохраняем лог
        if conversation_history["messages"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{LOGS_DIR}/recruiter_training_{timestamp}.json"
            
            # Формируем финальный лог
            final_log = {
                "timestamp": conversation_history["timestamp"],
                "position": position,
                "personality": personality,
                "experience": experience,
                "honesty": honesty,
                "random_profile": {
                    "type": selected_profile,
                    "description": profile_description
                },
                "messages": conversation_history["messages"]
            }
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(final_log, f, ensure_ascii=False, indent=2) 
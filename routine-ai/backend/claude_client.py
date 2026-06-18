import os
from groq import Groq, AsyncGroq

_client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))
_async_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY", ""))

MODEL = "gemma2-9b-it"

SYSTEM_PROMPT = """너는 루틴 관리 개인 비서야. 사용자가 하루에 해야 할 루틴을 관리하도록 도와줘.

루틴 추가/삭제/조회 요청을 처리할 때는 반드시 응답 첫 줄에 JSON 액션을 포함해:
- 추가: {"action":"add","name":"루틴명","time":"HH:MM","repeat":"daily|weekdays|weekends","description":"설명(선택)"}
- 삭제: {"action":"delete","name":"루틴명"}
- 조회: {"action":"list"}
- 없으면: {"action":"none"}

중요: JSON의 name, description 값은 반드시 사용자가 말한 한국어 그대로 써줘. 유니코드 이스케이프(\uXXXX) 없이 실제 한글로 작성해.
그 다음 줄부터 사용자에게 보낼 자연스러운 한국어 확인 메시지를 써줘.
알림 메시지는 간결한 코치 스타일로: "운동. 지금 바로." 같은 형태.
시간이 명확하지 않으면 반드시 물어봐.
JSON은 항상 첫 번째 줄에만 넣어."""

NOTIFICATION_PROMPT = """너는 루틴 알림 메시지를 생성하는 역할이야.
다음 루틴에 대해 간결하고 동기부여가 되는 코치 스타일 알림 메시지를 한 문장으로 만들어줘.
예시: "스쿼트 20개. 지금 바로." / "독서 시작. 30분." / "물 한 잔. 마셔."
반드시 한국어로, 2문장 이내로."""


def generate_notification_message(routine_name: str, description: str = "") -> str:
    context = f"루틴: {routine_name}"
    if description:
        context += f" ({description})"
    response = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": NOTIFICATION_PROMPT},
            {"role": "user", "content": context},
        ],
    )
    return response.choices[0].message.content.strip()


async def stream_chat_async(messages: list):
    """Groq 스트리밍 응답을 async generator로 반환"""
    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": m["role"], "content": m["content"]} for m in messages
    ]

    stream = await _async_client.chat.completions.create(
        model=MODEL,
        messages=groq_messages,
        stream=True,
        temperature=0,
    )

    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

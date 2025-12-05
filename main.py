# main.py  ← 直接复制这一个文件就行
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dashscope import Generation
import os

app = FastAPI()

# 解决跨域（必须！）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 你的通义千问 Key（部署时用环境变量，安全！）
API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-本地测试可直接写这里")

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])

    # 步骤2+3：调用通义千问 qwen-max（流式）
    responses = Generation.call(
        model="qwen-max",
        messages=messages,
        stream=True,
        result_format="message",
        api_key=API_KEY
    )

    # 步骤4：流式返回给小程序（一个字一个字发）
    async def stream_generator():
        for resp in responses:
            delta = resp.output.choices[0].delta.get("content", "")
            for char in delta:        # 按字符切分 → 打字机效果超丝滑
                yield char
                await __import__('asyncio').sleep(0)  # 让出控制权

    return StreamingResponse(stream_generator(), media_type="text/plain")
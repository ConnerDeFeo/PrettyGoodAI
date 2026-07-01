from fastapi import WebSocket
from config import bedrock, CONVERSATION_MODEL, SYSTEM_PROMPT, MAX_OUTPUT_TOKENS
import json

def send_message(history: list):
    # Call AWS Bedrock API with streaming enabled for real-time token delivery
    response = bedrock.converse_stream(
        modelId=CONVERSATION_MODEL,
        messages=history,
        system=[{"text": SYSTEM_PROMPT}],
        inferenceConfig={"maxTokens": MAX_OUTPUT_TOKENS},
    )
    return response["stream"]
    
async def recieve_message(websocket: WebSocket, stream):
    assistant_text = ""

    # Stream tokens to client as they arrive from the model
    for chunk in stream:
        token = chunk.get("contentBlockDelta", {}).get("delta", {}).get("text", "")
        if token:
            assistant_text += token
            await websocket.send_text(json.dumps({
                "type": "text",
                "token": token,
                "last": False
            }))

    # Send completion signal to client
    await websocket.send_text(json.dumps({
        "type": "text",
        "token": "",
        "last": True
    }))

    return assistant_text
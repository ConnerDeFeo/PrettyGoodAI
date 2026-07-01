from fastapi import WebSocket, Logger
import json
from config import *

async def websocket_handler(websocket: WebSocket, logger: Logger):
    await websocket.accept()
    call_sid = None
    history: list = []  # Maintains conversation history for context in Bedrock API
    is_processing = False  # Prevents concurrent processing of multiple prompts

    try:
        async for message in websocket.iter_text():
            # Skip processing if already handling a prompt to avoid race conditions
            if is_processing:
                continue

            data = json.loads(message)
            event = data.get("type")

            if event == "setup":
                # Extract call metadata from Twilio on connection initialization
                call_sid = data.get("callSid")

            elif event == "prompt":
                # Process user voice input and generate AI response
                user_text = data.get("voicePrompt", "").strip()
                if not user_text:
                    continue

                is_processing = True

                try:
                    # Add user message to conversation history
                    history.append({"role": "user", "content": [{"text": user_text}]})

                    # Call AWS Bedrock API with streaming enabled for real-time token delivery
                    response = bedrock.converse_stream(
                        modelId=CONVERSATION_MODEL,
                        messages=history,
                        system=[{"text": SYSTEM_PROMPT}],
                        inferenceConfig={"maxTokens": MAX_OUTPUT_TOKENS},
                    )

                    stream = response["stream"]
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

                    # Append complete assistant response to history for next turn
                    history.append({"role": "assistant", "content": [{"text": assistant_text}]})
                finally:
                    # Always reset processing flag even if an error occurs
                    is_processing = False

    except Exception as e:
        logger.exception(f"Unhandled error in websocket_handler: {e}")
    finally:
        # Clean up WebSocket connection on disconnect or error
        try:
            await websocket.close()
        except RuntimeError:
            # Socket may already be closed; ignore RuntimeError
            pass
from fastapi import WebSocket, Logger
import json
from dynamo import save_conversation_history
from conversation import *

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

                    # Get response from the AI
                    stream = await send_message(history)
                    assistant_text = await recieve_message(websocket, stream)

                    # Append complete assistant response to history for next turn
                    history.append({"role": "assistant", "content": [{"text": assistant_text}]})
                finally:
                    # Always reset processing flag even if an error occurs
                    is_processing = False

    except Exception as e:
        logger.exception(f"Unhandled error in websocket_handler: {e}")
    finally:
        # Clean up WebSocket connection on disconnect or error. Save conversation history
        save_conversation_history(call_sid, history)
        try:
            await websocket.close()
        except RuntimeError:
            # Socket may already be closed; ignore RuntimeError
            pass
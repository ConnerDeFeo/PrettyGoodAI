"""
Voice call routing and WebSocket handling for Twilio integration.
Manages Twilio handshakes and bidirectional voice conversation streaming via AWS Bedrock.
"""
import logging
from fastapi import APIRouter, WebSocket, Response
from twilio.twiml.voice_response import VoiceResponse, Connect, ConversationRelay
import json
from config import *

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(f"/handshake")
def ws_handshake():
    """Initialize Twilio voice connection with conversation relay settings."""
    response = VoiceResponse()
    connect = Connect()

    # Configure conversation relay with voice parameters (TTS, greeting, language)
    conversationrelay = ConversationRelay(url=f"wss://{SERVER_DOMAIN}")

    # Set language and voice provider (ElevenLabs) for text-to-speech
    conversationrelay.language(
        code="en-US",
        tts_provider="ElevenLabs",
        voice="gfRt6Z3Z8aTbpLfexQ7N",
    )
    connect.append(conversationrelay)
    response.append(connect)
    return Response(content=str(response), media_type="application/xml")

@router.websocket(f"/")
async def websocket_handler(websocket: WebSocket):
    """Handle bidirectional WebSocket communication for voice conversations."""
    await websocket.accept()
    call_sid = None
    history = []  # Maintains conversation history for context in Bedrock API
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
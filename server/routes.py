"""
Voice call routing and WebSocket handling for Twilio integration.
Manages Twilio handshakes and bidirectional voice conversation streaming via AWS Bedrock.
"""
import logging
from fastapi import APIRouter, WebSocket, Response
from twilio.twiml.voice_response import VoiceResponse, Connect, ConversationRelay
import json
from config import *
from websocket_handler import websocket_handler

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(f"/twiml")
def twiml():
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
async def websocket_router(websocket: WebSocket):
    """Handle bidirectional WebSocket communication for voice conversations."""
    return await websocket_handler(websocket, logger)
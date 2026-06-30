import logging
from fastapi import APIRouter, WebSocket, Response
from twilio.twiml.voice_response import VoiceResponse, Connect, ConversationRelay

router = APIRouter()
logger = logging.getLogger(__name__)

# Personal routes
@router.post(f"/handshake")
def ws_handshake():
    response = VoiceResponse()
    connect = Connect()
    conversationrelay = ConversationRelay(
        url="MOCK URL",
        welcome_greeting="MOCK GREETING",
        welcome_greeting_interruptible = False
    )
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
    await websocket.accept()
    call_sid = None
    phone_number = None
    history = []
    is_processing = False
import time
import logging
from config import conversation_history
    

logger = logging.getLogger(__name__)

def save_conversation_history(call_sid: str, history: list):
    conversation_history.put_item(Item={
        "call_sid": call_sid,
        "history": history
    })
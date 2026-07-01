# make_call.py
import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_PHONE_NUMBER")

TARGET_NUMBER = "+18054398008"

client = Client(account_sid, auth_token)

call = client.calls.create(
    to=TARGET_NUMBER,
    from_=from_number,
    url="https://pgai.connerdefeo.com/twiml"
)

print(f"Call initiated: {call.sid}")
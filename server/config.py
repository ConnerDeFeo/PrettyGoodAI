import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
conversation_history = dynamodb.Table("pgai_conversation_history")
bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")

SERVER_DOMAIN = ""
CONVERSATION_MODEL = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
SYSTEM_PROMPT = ""
MAX_OUTPUT_TOKENS = 300
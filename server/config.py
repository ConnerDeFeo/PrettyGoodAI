import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
conversation_history = dynamodb.Table("pretty_good_ai_conversation_history")
bedrock = boto3.client("bedrock-runtime", region_name="us-east-2")

CONVERSATION_MODEL = "Claude-haiku"
SYSTEM_PROMPT = ""
MAX_OUTPUT_TOKENS = 400
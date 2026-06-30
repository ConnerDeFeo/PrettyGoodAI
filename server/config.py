import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
conversation_history = dynamodb.Table("pretty_good_ai_conversation_history")
call_information = dynamodb.Table("pretty_good_ai_call_information")
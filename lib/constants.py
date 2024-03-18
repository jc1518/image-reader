# Region and model config
BEDROCK_REGION = "us-west-2"
BOTO_CONFIG = {"max_attempts": 3, "mode": "standard"}
ANTHROPIC_VERSION = "bedrock-2023-05-31"
MODEL_IDS = [
    "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
]
MAX_TOKENS = 2000
TEMPERATURE = 0
# MODEL_ARGS = {"temperature": 0, "max_tokens": 1000}

DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant with perfect vision and pay great attention to detail which makes you an expert at reading objects in images."
DEFAULT_PROMPT = "What are in the picture?"

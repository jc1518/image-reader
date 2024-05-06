# Region setting
BEDROCK_REGION = "us-west-2"
BOTO_CONFIG = {"max_attempts": 3, "mode": "standard"}

# Anthropic setting
ANTHROPIC_VERSION = "bedrock-2023-05-31"
MODEL_IDS = [
    "anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-3-sonnet-20240229-v1:0",
    "anthropic.claude-3-opus-20240229-v1:0",
]
MAX_TOKENS = 2000
TEMPERATURE = 0
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant with perfect vision and pay great attention to detail which makes you an expert at reading objects in images."
DEFAULT_PROMPT = "What are in the picture?"

# Titan multimodal embed setting
MM_EMBED_MODEL = "amazon.titan-embed-image-v1"
OUTPUT_EMBEDDING_LENGTH = 1024

# Titan image generator setting
IMAGE_GENERATOR_MODEL = "amazon.titan-image-generator-v1"
NUMBER_OF_IMAGES = 1
QUALITY = "standard"
CFG_SCALE = 8.0
HEIGHT = 512
WIDTH = 512
SEED = 0
IMAGE_NUMBERS = [1, 2, 3, 4, 5]
IMAGE_SIZE = [
    (1024, 1024),
    (768, 768),
    (512, 512),
    (768, 1152),
    (384, 576),
    (1152, 768),
    (576, 384),
    (768, 1280),
    (384, 640),
    (1280, 768),
    (640, 384),
    (896, 1152),
    (448, 576),
    (1152, 896),
    (576, 448),
    (768, 1408),
    (384, 704),
    (1408, 768),
    (704, 384),
    (640, 1408),
    (320, 704),
    (1408, 640),
    (704, 320),
    (1152, 640),
    (1173, 640),
]

# Chroma setting
COLLECTION_NAME = "image_library"
N_RESULTS = 1

# Persistent storage setting
DATA_LOCATION = "./data"
VECTOR_LOCATION = f"{DATA_LOCATION}/vector"
FILE_LOCATION = f"{DATA_LOCATION}/file"
TEMP_LOCATION = f"{DATA_LOCATION}/temp"

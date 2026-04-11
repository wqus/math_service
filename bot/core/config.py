import os
from dotenv import load_dotenv

env_file = os.getenv("ENV_FILE")  # ENV_FILE=".env.dev" или ".env.prod"
if env_file:
    load_dotenv(env_file)

MODE = os.getenv('MODE')

TOKEN = os.getenv('TOKEN')

LOCAL_WEBHOOK_HOST = os.getenv('LOCAL_WEBHOOK_HOST')
LOCAL_WEBHOOK_PORT = os.getenv('LOCAL_WEBHOOK_PORT')

WEBHOOK_PATH = os.getenv('WEBHOOK_PATH')
WEBHOOK_BASE_URL = os.getenv('WEBHOOK_BASE_URL')

WEBHOOK_URL_FULL_PATH = WEBHOOK_BASE_URL + WEBHOOK_PATH

REDIS_HOST = os.getenv('REDIS_HOST')

POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB=os.getenv('POSTGRES_DB')
POSTGRES_USER=os.getenv('POSTGRES_USER')

LLM_URL = os.getenv('LLM_URL')
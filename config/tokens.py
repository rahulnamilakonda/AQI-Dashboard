import dotenv
import os

dotenv.load_dotenv(".env")
os.getenv("WAQI_TOKEN")


OPENAQ_TOKEN = os.getenv("OPENAQ_TOKEN")
WAQI_TOKEN = os.getenv("WAQI_TOKEN")

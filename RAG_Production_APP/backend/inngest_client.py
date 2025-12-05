# inngest_client.py
import os
import logging
import datetime
import inngest
from dotenv import load_dotenv

load_dotenv()


# Make sure you read from env
INNGEST_BASE_URL = os.getenv("INNGEST_DEV_HOST")
if not INNGEST_BASE_URL:
    raise RuntimeError("INNGEST_DEV_HOST environment variable not set")

# Initialize Inngest client
inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer() 
)

import os
from dotenv import load_dotenv

load_dotenv()

# Ollama Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))
OLLAMA_KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "30m")

# Agent Configuration
AGENT_EVENT_LIMIT = int(os.getenv("AGENT_EVENT_LIMIT", "12"))

# Camera Configuration
CAMERA_SOURCE = os.getenv("CAMERA_SOURCE", "https://wzmedia.dot.ca.gov/D11/C214_SB_5_at_Via_De_San_Ysidro.stream/playlist.m3u8")
CAMERA_RECONNECT_SECONDS = int(os.getenv("CAMERA_RECONNECT_SECONDS", "5"))

# Database Configuration
DATABASE_PATH = "detections.db"

# Target Classes for YOLO
TARGET_CLASSES = ["person", "car", "truck", "bus", "motorcycle"]

# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
CAPTURES_DIR = os.path.join(STATIC_DIR, "captures")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

# Ensure directories exist
for directory in [STATIC_DIR, CAPTURES_DIR, UPLOADS_DIR]:
    os.makedirs(directory, exist_ok=True)

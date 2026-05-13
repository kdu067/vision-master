from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from services.config import TEMPLATES_DIR, STATIC_DIR
from services.event_repository import EventRepository
from services.ollama_client import OllamaClient
from services.monitoring_agent import MonitoringAgent
from services.video_monitor import VideoMonitor
from services.schemas import ChatRequest, EventResponse, AgentStatusResponse
import cv2
import numpy as np
import io

# Inicializar aplicação
app = FastAPI(title="AgroVision AI", version="1.0.0")

# Montar diretórios estáticos
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Instâncias de serviços
event_repo = EventRepository()
ollama = OllamaClient()
agent = MonitoringAgent()
video_monitor = VideoMonitor()

# Iniciar monitoramento de vídeo na startup
@app.on_event("startup")
async def startup_event():
    video_monitor.start()
    print("AgroVision AI iniciado")

@app.on_event("shutdown")
async def shutdown_event():
    video_monitor.stop()
    print("AgroVision AI finalizado")

# ============= ROTAS DE SAÚDE =============

@app.get("/health")
async def health():
    """Verificar saúde da aplicação"""
    return {
        "status": "ok",
        "ollama_available": ollama.is_available(),
        "camera_connected": video_monitor.is_connected
    }

# ============= ROTAS DE CÂMERA =============

@app.get("/camera/status")
async def camera_status():
    """Status da câmera"""
    return video_monitor.get_status()

@app.get("/frame")
async def get_current_frame():
    """Obter frame atual em JPEG"""
    frame = video_monitor.get_frame()
    if frame is None:
        return {"error": "Nenhum frame disponível"}
    
    success, buffer = cv2.imencode('.jpg', frame)
    if not success:
        return {"error": "Erro ao codificar frame"}
    
    return StreamingResponse(io.BytesIO(buffer.tobytes()), media_type="image/jpeg")

@app.get("/video_feed")
async def video_feed():
    """Stream MJPEG da câmera"""
    def generate():
        while True:
            frame = video_monitor.get_frame()
            if frame is None:
                continue
            
            success, buffer = cv2.imencode('.jpg', frame)
            if success:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n'
                       b'Content-Length: ' + str(len(buffer)).encode() + b'\r\n\r\n'
                       + buffer.tobytes() + b'\r\n')
    
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

# ============= ROTAS DE EVENTOS =============

@app.get("/events")
async def get_events(limit: int = 12):
    """Lista de eventos recentes"""
    events = event_repo.get_recent_events(limit)
    return events

@app.get("/events/count")
async def events_count():
    """Contar eventos"""
    return {"total": event_repo.count_events()}

# ============= ROTAS DO AGENTE =============

@app.get("/agent/status")
async def agent_status():
    """Status do agente"""
    events = event_repo.get_recent_events(12)
    status = agent.get_status(events)
    return status

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat com o agente"""
    try:
        events = event_repo.get_recent_events(12)
        
        # Montar mensagens do agente
        history = [{"role": msg.role, "content": msg.content} for msg in request.history] if request.history else []
        messages = agent.build_agent_messages(request.question, history, events)
        
        # Enviar para Ollama em streaming
        async def stream_response():
            response_text = ""
            try:
                for chunk in ollama.chat(messages, stream=True):
                    response_text += chunk
                    yield f"data: {chunk}\n\n"
                
                # Enviar evento final
                yield f"data: [DONE]\n\n"
            except Exception as e:
                yield f"data: Erro: {str(e)}\n\n"
        
        return StreamingResponse(stream_response(), media_type="text/event-stream")
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# ============= ROTAS DO DASHBOARD =============

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal"""
    return templates.TemplateResponse("index.html", {"request": request})

# ============= INICIALIZAR =============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

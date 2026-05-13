# 🚀 Guia Avançado - AgroVision AI

## 📚 Sumário
1. Customização do Agente
2. Trocar Modelos YOLO
3. Usar Modelos Ollama Diferentes
4. Integrar Câmeras IP Reais
5. Expandir Detecções
6. Monitoramento e Logs
7. Deployment em Produção

---

## 1️⃣ Customização do Agente

### Mudar Identidade do Agente

Edite `services/monitoring_agent.py`:

```python
AGENT_PROFILE = AgentProfile(
    name="Agente SeuNome",
    role="seu papel aqui",
    goal="seu objetivo aqui"
)
```

### Mudar Regras de Comportamento

Na mesma classe, customize o `build_system_prompt()`:

```python
def build_system_prompt(self) -> str:
    return (
        f"Você é o {self.profile.name}. "
        "Regra 1: sempre cite confiança. "
        "Regra 2: fale em português. "
        # Adicione suas regras aqui
    )
```

### Alterar Contexto Enviado

Customize `build_event_context()`:

```python
def build_event_context(self, events: List[Dict]) -> str:
    # Adicione métricas extras
    # Mude o formato
    # Adicione análises
```

---

## 2️⃣ Trocar Modelos YOLO

### Usar um Modelo Maior (Mais Preciso)

No `services/video_monitor.py`:

```python
# Antes (nano - rápido)
self.model = YOLO("yolo11n.pt")

# Depois (pequeno)
self.model = YOLO("yolo11s.pt")

# Ou (médio - recomendado)
self.model = YOLO("yolo11m.pt")
```

### Treinar Modelo Customizado

```python
from ultralytics import YOLO

# Treinar com seu dataset
model = YOLO("yolo11n.pt")
results = model.train(
    data="dataset_agro/data.yaml",
    epochs=100,
    imgsz=640,
    device=0  # GPU 0
)

# Usar modelo treinado
model = YOLO("runs/detect/train/weights/best.pt")
```

---

## 3️⃣ Usar Modelos Ollama Diferentes

### Listar Modelos Disponíveis

```bash
ollama list
```

### Baixar Outro Modelo

```bash
# Modelo menor (mais rápido)
ollama pull llama3.2:3b

# Ou outro modelo
ollama pull mistral
ollama pull neural-chat
```

### Usar no .env

```env
OLLAMA_MODEL=llama3.2:3b
# ou
OLLAMA_MODEL=mistral
```

### Testar Modelo Local

```bash
ollama run llama3
# e conversar direto
```

---

## 4️⃣ Integrar Câmeras IP Reais

### Câmera IP com RTSP

```env
CAMERA_SOURCE=rtsp://usuario:senha@192.168.1.100:554/stream1
```

### Câmera IP com HTTP

```env
CAMERA_SOURCE=http://192.168.1.100:8080/mjpeg.cgi
```

### Verificar Câmera

```bash
# Testar com ffplay
ffplay rtsp://usuario:senha@192.168.1.100:554/stream1

# Ou com OpenCV
python -c "
import cv2
cap = cv2.VideoCapture('rtsp://...')
ret, frame = cap.read()
print('Conectado!' if ret else 'Erro')
"
```

### Câmeras Públicas Testadas

- **Caltrans (CA)**: `https://wzmedia.dot.ca.gov/D11/C214_SB_5_at_Via_De_San_Ysidro.stream/playlist.m3u8`
- **CCTV Washington DC**: Vários feeds disponíveis
- **Webcams públicas**: webcamtaxi.com, earthcam.com

---

## 5️⃣ Expandir Detecções

### Adicionar Novas Classes

Edite `services/config.py`:

```python
TARGET_CLASSES = [
    "person",      # Já existe
    "car",         # Já existe
    "truck",       # Já existe
    "dog",         # Novo
    "cat",         # Novo
    "bicycle",     # Novo
]
```

### Filtrar por Confiança

Em `services/video_monitor.py`:

```python
if label in TARGET_CLASSES and confidence > 0.7:  # Aumentado de 0.5
    self._save_detection(frame, label, confidence)
```

### Contar Objetos Específicos

Customize `build_event_context()`:

```python
def build_event_context(self, events: List[Dict]) -> str:
    # Contar por classe
    counts = {}
    for event in events:
        label = event.get("label", "unknown")
        counts[label] = counts.get(label, 0) + 1
    
    # Encontrar classe mais frequente
    if counts:
        most_common = max(counts, key=counts.get)
        # Use essa informação
```

---

## 6️⃣ Monitoramento e Logs

### Adicionar Logging

Crie `services/logger.py`:

```python
import logging
import os

log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "agrovision.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AgroVision")
```

### Usar em Serviços

```python
from services.logger import logger

# Em video_monitor.py
logger.info(f"Detectado: {label} com confiança {confidence}")

# Em ollama_client.py
logger.debug(f"Enviando para Ollama: {len(messages)} mensagens")
```

### Monitorar Performance

```python
import time

start = time.time()
# ... código ...
elapsed = time.time() - start
logger.info(f"Operação levou {elapsed:.2f}s")
```

---

## 7️⃣ Deployment em Produção

### 1. Usar Gunicorn (Production Server)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### 2. Usar Docker

Crie `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build e execute:

```bash
docker build -t agrovision-ai .
docker run -p 8000:8000 agrovision-ai
```

### 3. Variáveis de Ambiente

Em produção, use variáveis de ambiente em vez de .env:

```bash
export OLLAMA_URL=http://ollama-service:11434/api/chat
export OLLAMA_MODEL=llama3
export CAMERA_SOURCE=rtsp://production-camera/stream
```

### 4. HTTPS/SSL

Use Nginx como proxy:

```nginx
server {
    listen 443 ssl;
    server_name agrovision.seu-dominio.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. Banco de Dados Persistente

Mude para PostgreSQL em `services/event_repository.py`:

```python
import psycopg2

class EventRepository:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS")
        )
```

### 6. Cache com Redis

```python
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

# Cachear respostas do agente
def get_cached_response(key):
    return cache.get(key)

def set_cached_response(key, value):
    cache.setex(key, 3600, value)  # 1 hora
```

---

## 🔧 Otimizações Práticas

### Para Máquinas Fracas

```env
# Modelo YOLO nano
CAMERA_RECONNECT_SECONDS=10

# Modelo Ollama pequeno
OLLAMA_MODEL=llama3.2:3b
OLLAMA_KEEP_ALIVE=10m

# Menos eventos em contexto
AGENT_EVENT_LIMIT=5
```

### Para Máquinas Potentes

```env
# Modelo YOLO médio
# Detecções mais frequentes
# Mais eventos em contexto
AGENT_EVENT_LIMIT=20

# Modelo Ollama maior
OLLAMA_MODEL=llama3
```

### Cachear Frames

```python
# Em video_monitor.py
from functools import lru_cache

@lru_cache(maxsize=2)
def process_frame_cached(self, frame_hash):
    # Evita reprocessar frames idênticos
```

---

## 📊 Métricas para Monitorar

1. **Latência do YOLO**: Tempo para detectar objetos
2. **Latência do Ollama**: Tempo para gerar resposta
3. **Taxa de detecção**: % de frames com detecções
4. **Confiança média**: Média de confiança das detecções
5. **Tamanho do BD**: Quantos eventos armazenados
6. **Uptime da câmera**: Tempo de conexão contínua

---

## 🎓 Exemplos de Extensão

### Alertas por Email

```python
import smtplib

def send_alert(label, confidence):
    if confidence > 0.95:
        msg = f"ALERTA: {label} detectado com {confidence:.0%}"
        # enviar email
```

### Webhook para Slack

```python
import requests

def post_to_slack(message):
    requests.post(
        "https://hooks.slack.com/...",
        json={"text": message}
    )
```

### Integrar com API Externa

```python
def send_to_analytics(event):
    requests.post(
        "https://api-externa.com/events",
        json=event,
        headers={"Authorization": "Bearer TOKEN"}
    )
```

---

## 📞 Debugging

### Ver Logs do Ollama

```bash
ollama serve
# Em outro terminal, faça requisições
```

### Debug Python

```bash
python -m pdb app.py
# ou use breakpoint()
```

### Inspecionar BD

```bash
sqlite3 detections.db
> SELECT * FROM events LIMIT 5;
> SELECT label, COUNT(*) FROM events GROUP BY label;
```

---

Sucesso com suas customizações! 🎉


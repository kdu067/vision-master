# 🔧 Troubleshooting - AgroVision AI

Guia completo de solução de problemas com exemplos e comandos.

---

## ❌ PROBLEMA: Python não está instalado ou não aparece no PATH

### Sintomas
```
'python' is not recognized as an internal or external command
```

### Solução

**Windows:**
1. Desinstale Python completamente
2. Baixe Python 3.11.15 de https://www.python.org/downloads
3. **Importante**: Marcar "Add Python to PATH" durante instalação
4. Abra novo terminal e teste:
```bash
python --version
pip --version
```

**Linux/macOS:**
```bash
sudo apt install python3.11  # Ubuntu/Debian
brew install python@3.11     # macOS
```

---

## ❌ PROBLEMA: Ambiente virtual não ativa

### Sintomas
```
The term '.\\.venv\Scripts\Activate.ps1' is not recognized
```

### Solução

**Windows PowerShell:**
```bash
# 1. Permitir scripts (apenas nessa sessão)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 2. Tentar ativar novamente
.\.venv\Scripts\Activate.ps1

# Ou usar Command Prompt (cmd.exe) em vez de PowerShell
.\.venv\Scripts\activate.bat
```

**Se persistir:**
```bash
# Recriar .venv
rmdir .venv
python -m venv .venv

# Ativar
.\.venv\Scripts\Activate.ps1
```

---

## ❌ PROBLEMA: Módulos não encontrados após instalar

### Sintomas
```
ModuleNotFoundError: No module named 'fastapi'
```

### Solução

```bash
# 1. Verificar que .venv está ativo (verá "(.venv)" no prompt)
# 2. Reinstalar dependências
pip install -r requirements.txt

# 3. Se ainda não funcionar
pip install --upgrade pip
pip install --force-reinstall -r requirements.txt

# 4. Verificar se foi instalado
pip list | grep fastapi
```

---

## ❌ PROBLEMA: Ollama não está disponível

### Sintomas
```
Erro ao conectar com Ollama: Connection refused
```

### Diagnóstico

```bash
# 1. Verificar se está instalado
ollama --version

# 2. Verificar se está rodando
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags

# 3. Verificar porta
netstat -ano | findstr :11434  # Windows
lsof -i :11434                 # Linux/macOS
```

### Solução

**Se não está instalado:**
1. Ir para https://ollama.com/download
2. Baixar e instalar
3. Abrir novo terminal

**Se está instalado mas não rodando:**
```bash
# Iniciar Ollama
ollama serve

# Deixar rodando e abrir outro terminal para o projeto
```

**Se quer rodar Ollama em porta diferente:**
```bash
ollama serve --addr 127.0.0.1:9090
# Depois atualizar .env
OLLAMA_URL=http://127.0.0.1:9090/api/chat
```

---

## ❌ PROBLEMA: Modelo Ollama não encontrado

### Sintomas
```
Error: pull model manifest: path does not match any models
model 'llama3' not found
```

### Solução

```bash
# 1. Verificar quais modelos tem
ollama list

# 2. Se llama3 não aparecer, baixar
ollama pull llama3

# 3. Se internet lenta, tente modelo menor
ollama pull llama3.2:3b

# 4. Depois atualizar .env
OLLAMA_MODEL=llama3.2:3b
```

**Modelos recomendados:**
- Rápido: `llama3.2:1b` (800 MB)
- Balanceado: `llama3.2:3b` (2 GB)
- Melhor: `llama3` (4 GB)

---

## ❌ PROBLEMA: Câmera não conecta

### Sintomas
```
{
  "online": false,
  "connected": false,
  "has_live_frame": false
}
```

### Diagnóstico

```bash
# 1. Testar URL da câmera no navegador
# Ir para: https://wzmedia.dot.ca.gov/...

# 2. Testar com ffmpeg
ffmpeg -i "https://wzmedia.dot.ca.gov/..." -f null -
# Deve exibir informações ou erro

# 3. Testar com OpenCV
python -c "
import cv2
cap = cv2.VideoCapture('https://...')
ret, frame = cap.read()
print('OK' if ret else 'ERRO')
cap.release()
"
```

### Solução

**Se URL é webcam local (0 ou 1):**
```python
# Verificar números de câmeras
import cv2
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f'Câmera {i} disponível')
    cap.release()
```

**Se URL é stream público:**
- Testar URL no navegador primeiro
- Verificar se precisa de credenciais
- Testar com VLC player
- Verificar se é HTTP ou RTSP

**Se URL é câmera IP privada:**
```env
# Adicionar credenciais na URL
CAMERA_SOURCE=rtsp://usuario:senha@192.168.1.100:554/stream

# Ou sem credenciais
CAMERA_SOURCE=rtsp://192.168.1.100:554/stream
```

**Esperar conexão estabilizar:**
```python
# Em services/video_monitor.py, aumentar timeout
# O OpenCV tenta várias vezes
```

---

## ❌ PROBLEMA: YOLO não detecta objetos

### Sintomas
```
GET /events retorna lista vazia
```

### Diagnóstico

```bash
# 1. Verificar se câmera está conectada
GET http://127.0.0.1:8000/camera/status

# 2. Verificar se há frames
GET http://127.0.0.1:8000/frame
# Deve exibir imagem

# 3. Testar YOLO manualmente
python -c "
from ultralytics import YOLO
model = YOLO('yolo11n.pt')
results = model.predict('sua_imagem.jpg')
print(results[0])
"
```

### Solução

**YOLO não carrega:**
```bash
# Reinstalar Ultralytics
pip install --upgrade ultralytics

# Testar modelo
python -c "from ultralytics import YOLO; YOLO('yolo11n.pt').predict('test.jpg')"
```

**YOLO detecta mas salva poucos eventos:**
- Baixar confiança em `services/video_monitor.py`
- Alterar de `confidence > 0.5` para `confidence > 0.3`

**YOLO muito lento:**
- Usar modelo nano: `yolo11n.pt`
- Reduzir resolução em `services/video_monitor.py`
- Processar só 1 a cada N frames

**YOLO detecta errado:**
- Treinar modelo próprio (ver GUIA_AVANCADO.md)
- Usar modelo diferente (yolo11s, yolo11m)

---

## ❌ PROBLEMA: Agente responde genérico

### Sintomas
```
Resposta: "Olá! Como posso ajudar?"
(em vez de análise operacional)
```

### Diagnóstico

```bash
# 1. Verificar status do agente
GET http://127.0.0.1:8000/agent/status

# Se events_in_context = 0:
# Problema: não há eventos detectados
# Solução: esperar YOLO detectar algo

# Se events_in_context > 0:
# Problema: Ollama não está usando contexto
# Solução: ver abaixo
```

### Solução

**Aguardar detecções:**
- YOLO precisa de tempo para detectar
- Deixar câmera ligada por alguns minutos
- Fazer perguntas após eventos aparecerem em `/events`

**Se há eventos mas resposta é genérica:**
```python
# Em services/monitoring_agent.py
# Verificar se contexto está sendo enviado

# Adicionar debug
def build_agent_messages(self, question, history, events):
    messages = [...]
    print(f"DEBUG: Enviando {len(events)} eventos")
    print(f"DEBUG: Contexto: {messages[1]['content'][:100]}")
    return messages
```

**Ollama pode não estar entendendo instrução:**
- Testar com pergunta simples: "Quantos eventos há?"
- Verificar se modelo é llama3 (recomendado)
- Tentar modelo diferente

---

## ❌ PROBLEMA: Dashboard não carrega

### Sintomas
```
Página branca
Erro 404 no console
```

### Diagnóstico

```bash
# 1. Verificar se FastAPI está rodando
GET http://127.0.0.1:8000/health

# 2. Verificar se template existe
# Arquivo: templates/index.html deve existir

# 3. Ver logs do terminal
# Deve exibir "Uvicorn running on"

# 4. Verificar porta
netstat -ano | findstr :8000
```

### Solução

**FastAPI não rodando:**
```bash
# Confirmar que está no diretório correto
cd C:\projetos\agrovision_ia

# Confirmação que .venv está ativo
# (deve haver "(.venv)" no prompt)

# Rodar novamente
python -m uvicorn app:app --reload
```

**Template não encontrado:**
```bash
# Verificar arquivo
dir templates\index.html

# Se não existir, recriá-lo
# Copiar conteúdo de templates/index.html
```

**Porta 8000 já em uso:**
```bash
# Usar porta diferente
python -m uvicorn app:app --port 8001

# Abrir em http://127.0.0.1:8001
```

---

## ❌ PROBLEMA: Chat não funciona (resposta vazia)

### Sintomas
```
Envia pergunta → nada acontece
```

### Diagnóstico

```bash
# 1. Verificar Ollama
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags

# 2. Fazer teste via curl
curl -X POST http://127.0.0.1:11434/api/chat `
  -H "Content-Type: application/json" `
  -d '{
    "model": "llama3",
    "messages": [{"role": "user", "content": "olá"}]
  }'
```

### Solução

**Se Ollama não responde:**
- Consultar seção "Ollama não está disponível" acima

**Se há timeout:**
```env
# Aumentar timeout em .env
OLLAMA_TIMEOUT=300
```

**Se resposta está lenta:**
```bash
# Ver logs do Ollama
# O terminal onde rodou "ollama serve" deve mostrar atividade

# Modelo pode estar carregando primeira vez
# Aguardar 30-60 segundos

# Próximas requisições serão mais rápidas
```

---

## ❌ PROBLEMA: Banco de dados corrupto

### Sintomas
```
database disk image is malformed
UNIQUE constraint failed
```

### Solução

```bash
# 1. Fazer backup
copy detections.db detections.db.backup

# 2. Deletar banco
del detections.db

# 3. Reiniciar aplicação
# Novo banco será criado automaticamente
python -m uvicorn app:app --reload
```

---

## ❌ PROBLEMA: Memória insuficiente

### Sintomas
```
MemoryError
Aplicação trava frequentemente
```

### Solução

**Reduzir consumo:**
```env
# Usar modelo YOLO menor
# (já é yolo11n, o nano)

# Usar modelo Ollama menor
OLLAMA_MODEL=llama3.2:1b

# Reduzir limite de eventos
AGENT_EVENT_LIMIT=5
```

**Limpar banco:**
```bash
# Manter apenas últimos 1000 eventos
sqlite3 detections.db "DELETE FROM events WHERE id < (SELECT MAX(id) - 1000 FROM events)"
```

---

## ❌ PROBLEMA: CPU em 100%

### Sintomas
```
Ventilador muito alto
Computador lento
```

### Solução

**Reduzir frequência de processamento:**
```python
# Em services/video_monitor.py
# Processar 1 a cada N frames

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    frame_count += 1
    
    # Processar só 1 a cada 5 frames
    if frame_count % 5 == 0:
        self._process_frame(frame)
```

**Aumentar intervalo de reconexão:**
```env
CAMERA_RECONNECT_SECONDS=10
```

---

## ❌ PROBLEMA: Firewall bloqueia Ollama

### Sintomas
```
Connection refused
Connection timed out
```

### Solução

**Windows Defender:**
1. Abrir Windows Defender
2. Ir para "Firewall & network protection"
3. "Allow an app through firewall"
4. Encontrar Ollama e permitir

**Outra opção:**
```bash
# Rodar Ollama em localhost apenas (padrão)
ollama serve
# Não precisa liberar porta para internet
```

---

## 📋 Checklist de Debugging

Quando algo não funciona:

- [ ] Python 3.11 instalado? `python --version`
- [ ] .venv ativo? `(deve haver (.venv) no prompt)`
- [ ] Dependências instaladas? `pip list | grep fastapi`
- [ ] Ollama rodando? `curl http://127.0.0.1:11434/api/tags`
- [ ] Modelo baixado? `ollama list`
- [ ] Câmera conecta? `/camera/status` retorna online=true
- [ ] FastAPI rodando? `http://127.0.0.1:8000`
- [ ] Há eventos? `/events` tem dados
- [ ] Agente tem contexto? `/agent/status` shows events_in_context > 0

---

## 📞 Pedindo Ajuda

Se problema persistir, forneça:

1. **Sistema**: Windows/Linux/macOS, versão
2. **Versões**: Python, Ollama, YOLO
3. **Erro exato**: Copiar mensagem completa
4. **O que já tentou**: Passos executados
5. **Logs**: Terminal output, se possível

Bom debug! 🐛🔍


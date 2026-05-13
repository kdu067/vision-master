# 🌾 AgroVision AI - Documentação Completa

Monitoramento e análise operacional com visão computacional e IA generativa local.

## 📋 Pré-requisitos

- **Python 3.11.15** (64 bits)
- **Ollama** instalado e rodando
- **Modelo llama3** baixado no Ollama
- **Windows 10/11**, Linux ou macOS

## 🚀 Instalação Rápida

### 1. Instalar Ollama
- Baixar em: https://ollama.com/download
- Instalar normalmente
- Depois, no terminal:
```bash
ollama pull llama3
```

### 2. Preparar Ambiente Python

```bash
# Ativar ambiente virtual
.\.venv\Scripts\Activate.ps1

# Instalar dependências
pip install -r requirements.txt
```

### 3. Rodar o Projeto

```bash
# Com Ollama já rodando em outro terminal:
python -m uvicorn app:app --reload

# Abrir no navegador:
# http://127.0.0.1:8000
```

## 📁 Estrutura do Projeto

```
agrovision_ia/
├── .env                      # Variáveis de ambiente
├── app.py                    # FastAPI principal
├── requirements.txt          # Dependências Python
├── services/
│   ├── __init__.py
│   ├── config.py            # Configurações
│   ├── schemas.py           # Modelos Pydantic
│   ├── event_repository.py  # SQLite para eventos
│   ├── ollama_client.py     # Cliente Ollama
│   ├── monitoring_agent.py  # Agente AgroVision
│   └── video_monitor.py     # Monitor YOLO
├── templates/
│   └── index.html           # Dashboard HTML
├── static/
│   ├── dashboard.css        # Estilos
│   ├── dashboard.js         # Interatividade
│   └── captures/            # Imagens capturadas
└── detections.db            # Banco SQLite (criado automaticamente)
```

## 🔧 Configuração (.env)

Edite o arquivo `.env` para personalizar:

```env
# Ollama
OLLAMA_URL=http://127.0.0.1:11434/api/chat
OLLAMA_MODEL=llama3

# Câmera (trocar por sua URL)
CAMERA_SOURCE=https://wzmedia.dot.ca.gov/D11/C214_SB_5_at_Via_De_San_Ysidro.stream/playlist.m3u8

# Agente
AGENT_EVENT_LIMIT=12
```

### Opções de Câmera

- Webcam local: `0` ou `1`
- Stream RTSP: `rtsp://192.168.1.100:554/stream`
- Stream HLS: `https://exemplo.com/stream.m3u8`
- Arquivo MP4: `video.mp4`

## 🎯 O que o Sistema Faz

### 1. **Câmera**
   - Lê câmera local ou pública autorizada
   - Processa frames continuamente
   - Reconecta automaticamente se cair

### 2. **YOLO11**
   - Detecta objetos: person, car, truck, bus, motorcycle
   - Confiança mínima: 50%
   - Salva frames com detecções

### 3. **SQLite**
   - Armazena eventos: label, confiança, horário
   - Guarda caminho das imagens capturadas
   - Histórico consultável

### 4. **Agente AgroVision**
   - Interpreta eventos recentes
   - Analisa padrões
   - Explica riscos operacionais
   - Recomenda próximas ações

### 5. **Dashboard**
   - Feed ao vivo da câmera
   - Lista de eventos recentes
   - Chat com o agente
   - Status do sistema

## 📡 Rotas Principais

| Rota | Método | Descrição |
|------|--------|-----------|
| `/` | GET | Dashboard principal |
| `/health` | GET | Status da aplicação |
| `/camera/status` | GET | Status da câmera |
| `/video_feed` | GET | Stream MJPEG |
| `/frame` | GET | Frame atual em JPEG |
| `/events` | GET | Lista de eventos |
| `/agent/status` | GET | Status do agente |
| `/chat` | POST | Enviar pergunta ao agente |

## 💬 Exemplos de Perguntas para o Agente

- "O que foi detectado nos últimos eventos?"
- "Existe algum padrão no monitoramento?"
- "Avalie o risco operacional agora"
- "Qual deve ser a próxima ação?"
- "Resuma a situação em 3 pontos"

## 🛠 Solução de Problemas

### Ollama não responde
```bash
# Verificar se está rodando
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:11434/api/tags

# Se não funcionar, rodar manualmente
ollama serve
```

### Câmera não conecta
- Verificar URL em `.env`
- Testar URL no navegador
- Confirmar permissões/autorização

### Agente responde genérico
- Verifiquem `/agent/status`
- Se `events_in_context` for 0, não há eventos
- Aguardar detecções da câmera

### YOLO não carrega
```bash
# Reinstalar ultralytics
pip install --upgrade ultralytics

# Testar carregamento
python -c "from ultralytics import YOLO; YOLO('yolo11n.pt')"
```

## 📚 Conceitos Principais

### YOLO
Detecta objetos em imagens. Retorna: classe + confiança.

### Ollama
Roda modelo de linguagem local (llama3). Gera texto.

### Agente
Camada Python que organiza como o Ollama deve pensar:
- Define identidade e objetivo
- Fornece contexto dos eventos
- Mantém memória curta da conversa
- Orienta formato de resposta

### Sistema Completo
```
Câmera → YOLO → SQLite → Agente → Ollama → Dashboard
```

## ⚖️ Considerações Éticas e Legais

✅ **Faça**
- Use câmeras públicas oficiais
- Use câmeras privadas com autorização
- Fale sobre eventos, não pessoas
- Use para fins didáticos/operacionais legítimos

❌ **Não Faça**
- Identificação facial
- Tentativa de identificar pessoas
- Vigilância invasiva
- Armazenar dados sensíveis desnecessários

## 🚀 Próximas Evoluções

O agente pode evoluir para:
- Gerar alertas automáticos
- Classificar severidade
- Criar relatórios automáticos
- Enviar notificações
- Comparar padrões por horário
- Abrir chamados em outros sistemas

## 📞 Suporte

Problemas comuns estão em `/services` nos comentários do código.

Referência completa: Ver arquivos PDF da documentação anexados.

---

**AgroVision AI v1.0** | Desenvolvido para fins didáticos em Engenharia de Software

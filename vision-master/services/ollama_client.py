import requests
import json
from typing import List, Dict, Generator
from services.config import OLLAMA_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT

class OllamaClient:
    def __init__(self):
        self.url = OLLAMA_URL
        self.model = OLLAMA_MODEL
        self.timeout = OLLAMA_TIMEOUT
    
    def is_available(self) -> bool:
        """Verificar se Ollama está disponível"""
        try:
            response = requests.get(
                self.url.replace("/api/chat", "/api/tags"),
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def warmup(self):
        """Carregar modelo na memória"""
        try:
            self.chat(
                messages=[{"role": "user", "content": "oi"}],
                stream=False
            )
        except:
            pass
    
    def chat(self, messages: List[Dict], stream: bool = True) -> Generator[str, None, None] | str:
        """
        Enviar mensagens para Ollama
        
        Se stream=True, retorna generator com chunks
        Se stream=False, retorna texto completo
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }
        
        try:
            response = requests.post(
                self.url,
                json=payload,
                timeout=self.timeout,
                stream=stream
            )
            response.raise_for_status()
            
            if stream:
                return self._stream_response(response)
            else:
                data = response.json()
                return data.get("message", {}).get("content", "")
        except Exception as e:
            return f"Erro ao conectar com Ollama: {str(e)}"
    
    def _stream_response(self, response) -> Generator[str, None, None]:
        """Processar resposta em streaming"""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield content
                except:
                    pass

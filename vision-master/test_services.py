import pytest
from services.event_repository import EventRepository
from services.monitoring_agent import MonitoringAgent, AGENT_PROFILE
from services.ollama_client import OllamaClient
import tempfile
import os

# ============= TESTES DE REPOSITÓRIO =============

class TestEventRepository:
    
    @pytest.fixture
    def temp_db(self):
        """Criar banco de dados temporário para testes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            # Não usamos pois a classe já cria o db
            yield tmpdir
    
    def test_init_db(self, monkeypatch, temp_db):
        """Testar inicialização do banco"""
        db_path = os.path.join(temp_db, "test.db")
        monkeypatch.setattr("services.event_repository.DATABASE_PATH", db_path)
        
        repo = EventRepository()
        assert os.path.exists(db_path)
    
    def test_save_event(self, monkeypatch, temp_db):
        """Testar salvamento de evento"""
        db_path = os.path.join(temp_db, "test.db")
        monkeypatch.setattr("services.event_repository.DATABASE_PATH", db_path)
        
        repo = EventRepository()
        event_id = repo.save_event("car", 0.95, "/static/captures/test.jpg")
        
        assert isinstance(event_id, int)
        assert event_id > 0
    
    def test_get_recent_events(self, monkeypatch, temp_db):
        """Testar leitura de eventos recentes"""
        db_path = os.path.join(temp_db, "test.db")
        monkeypatch.setattr("services.event_repository.DATABASE_PATH", db_path)
        
        repo = EventRepository()
        repo.save_event("car", 0.95, "/static/captures/test1.jpg")
        repo.save_event("person", 0.87, "/static/captures/test2.jpg")
        
        events = repo.get_recent_events(limit=5)
        
        assert len(events) == 2
        assert events[0]["label"] in ["car", "person"]
    
    def test_count_events(self, monkeypatch, temp_db):
        """Testar contagem de eventos"""
        db_path = os.path.join(temp_db, "test.db")
        monkeypatch.setattr("services.event_repository.DATABASE_PATH", db_path)
        
        repo = EventRepository()
        repo.save_event("car", 0.95)
        repo.save_event("truck", 0.88)
        repo.save_event("person", 0.92)
        
        count = repo.count_events()
        assert count == 3

# ============= TESTES DO AGENTE =============

class TestMonitoringAgent:
    
    def test_agent_profile(self):
        """Testar perfil do agente"""
        assert AGENT_PROFILE.name == "Agente AgroVision"
        assert AGENT_PROFILE.role == "triagem operacional de eventos"
        assert "Analisar detecções recentes" in AGENT_PROFILE.goal
    
    def test_build_system_prompt(self):
        """Testar construção do prompt do sistema"""
        agent = MonitoringAgent()
        prompt = agent.build_system_prompt()
        
        assert "Agente AgroVision" in prompt
        assert "português do Brasil" in prompt
        assert "não invente dados" in prompt.lower()
    
    def test_build_event_context_empty(self):
        """Testar contexto com lista vazia"""
        agent = MonitoringAgent()
        context = agent.build_event_context([])
        
        assert "Nenhum evento" in context
    
    def test_build_event_context_with_events(self):
        """Testar contexto com eventos"""
        agent = MonitoringAgent()
        events = [
            {"label": "car", "confidence": 0.95, "event_time": "2026-04-15 10:00:00"},
            {"label": "person", "confidence": 0.87, "event_time": "2026-04-15 10:00:05"},
            {"label": "car", "confidence": 0.92, "event_time": "2026-04-15 10:00:10"},
        ]
        
        context = agent.build_event_context(events)
        
        assert "3" in context  # 3 eventos
        assert "car" in context
        assert "person" in context
        assert "0.9" in context  # confiança média
    
    def test_normalize_history(self):
        """Testar normalização do histórico"""
        agent = MonitoringAgent()
        history = [
            {"role": "user", "content": f"msg {i}"}
            for i in range(20)
        ]
        
        normalized = agent.normalize_history(history)
        
        # Deve limitar ao máximo
        assert len(normalized) <= agent.max_history
    
    def test_build_agent_messages(self):
        """Testar construção de mensagens do agente"""
        agent = MonitoringAgent()
        question = "O que está acontecendo?"
        history = [
            {"role": "user", "content": "Olá"},
            {"role": "assistant", "content": "Oi!"}
        ]
        events = [
            {"label": "car", "confidence": 0.95, "event_time": "2026-04-15 10:00:00"},
        ]
        
        messages = agent.build_agent_messages(question, history, events)
        
        # Deve ter: system prompt + system context + history + user question
        assert len(messages) >= 4
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == question
    
    def test_get_status(self):
        """Testar status do agente"""
        agent = MonitoringAgent()
        events = [
            {"label": "car", "confidence": 0.95, "event_time": "2026-04-15 10:00:00"},
        ]
        
        status = agent.get_status(events)
        
        assert status["name"] == "Agente AgroVision"
        assert status["events_in_context"] == 1
        assert "context_preview" in status

# ============= TESTES DO CLIENTE OLLAMA =============

class TestOllamaClient:
    
    def test_client_initialization(self):
        """Testar inicialização do cliente"""
        client = OllamaClient()
        
        assert client.url == "http://127.0.0.1:11434/api/chat"
        assert client.model == "llama3"
        assert client.timeout == 120
    
    def test_is_available_format(self):
        """Testar método is_available (apenas formato)"""
        client = OllamaClient()
        
        # Não podemos testar conectividade sem Ollama rodando
        # Mas podemos testar que o método não lança exceção
        result = client.is_available()
        assert isinstance(result, bool)

# ============= TESTES DE INTEGRAÇÃO =============

class TestIntegration:
    
    def test_workflow_detection_to_agent(self, monkeypatch, tmp_path):
        """Testar fluxo: detecção -> BD -> agente"""
        db_path = str(tmp_path / "test.db")
        monkeypatch.setattr("services.event_repository.DATABASE_PATH", db_path)
        
        # 1. Salvar eventos
        repo = EventRepository()
        repo.save_event("car", 0.95)
        repo.save_event("person", 0.87)
        
        # 2. Recuperar eventos
        events = repo.get_recent_events(limit=5)
        assert len(events) == 2
        
        # 3. Passar para agente
        agent = MonitoringAgent()
        context = agent.build_event_context(events)
        
        assert "2" in context
        assert "car" in context
        assert "person" in context

# ============= TESTES DE SCHEMAS =============

class TestSchemas:
    
    def test_chat_request_schema(self):
        """Testar schema de requisição de chat"""
        from services.schemas import ChatRequest, ChatMessage
        
        history = [
            ChatMessage(role="user", content="Olá"),
            ChatMessage(role="assistant", content="Oi!")
        ]
        
        request = ChatRequest(question="Como vai?", history=history)
        
        assert request.question == "Como vai?"
        assert len(request.history) == 2
    
    def test_event_response_schema(self):
        """Testar schema de resposta de evento"""
        from services.schemas import EventResponse
        
        event = EventResponse(
            id=1,
            event_time="2026-04-15 10:00:00",
            label="car",
            confidence=0.95,
            image_path="/static/captures/test.jpg"
        )
        
        assert event.id == 1
        assert event.label == "car"
        assert event.confidence == 0.95
    
    def test_agent_status_schema(self):
        """Testar schema de status do agente"""
        from services.schemas import AgentStatusResponse
        
        status = AgentStatusResponse(
            name="Agente AgroVision",
            role="triagem operacional",
            goal="Analisar eventos",
            events_in_context=5,
            context_preview="Preview..."
        )
        
        assert status.name == "Agente AgroVision"
        assert status.events_in_context == 5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

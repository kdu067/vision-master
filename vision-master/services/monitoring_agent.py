from dataclasses import dataclass
from typing import List, Dict
from services.config import AGENT_EVENT_LIMIT

@dataclass(frozen=True)
class AgentProfile:
    name: str
    role: str
    goal: str

# Perfil do agente
AGENT_PROFILE = AgentProfile(
    name="Agente AgroVision",
    role="triagem operacional de eventos",
    goal="Analisar detecções recentes, explicar riscos e sugerir a próxima ação."
)

class MonitoringAgent:
    def __init__(self):
        self.profile = AGENT_PROFILE
        self.max_history = 8
    
    def build_system_prompt(self) -> str:
        """Construir prompt do sistema para o agente"""
        return (
            f"Você é o {self.profile.name}, um agente de {self.profile.role}. "
            f"Objetivo: {self.profile.goal} "
            "Trate os dados como monitoramento operacional autorizado de ambiente real. "
            "Responda em português do Brasil, de forma direta e útil. "
            "Use os eventos fornecidos como fonte principal. "
            "Não invente dados que não aparecem no contexto. "
            "Não tente identificar pessoas; fale apenas sobre eventos, riscos e próximas ações. "
            "Quando fizer sentido, organize a resposta em: leitura, risco e recomendação."
        )
    
    def build_event_context(self, events: List[Dict]) -> str:
        """Transformar eventos em contexto operacional"""
        if not events:
            return "Nenhum evento registrado no momento."
        
        # Contar labels
        label_counts = {}
        for event in events:
            label = event.get("label", "unknown")
            label_counts[label] = label_counts.get(label, 0) + 1
        
        # Calcular confiança média
        confidences = [float(e.get("confidence", 0)) for e in events]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Montar contexto
        labels_str = ", ".join([f"{k}: {v}" for k, v in label_counts.items()])
        most_recent = events[0] if events else {}
        
        context = (
            f"Contexto operacional para o agente:\n"
            f"- Eventos considerados: {len(events)}\n"
            f"- Evento mais recente: {most_recent.get('label', 'N/A')} em {most_recent.get('event_time', 'N/A')}\n"
            f"- Distribuição recente: {labels_str}\n"
            f"- Confiança média: {avg_confidence:.2f}\n"
            f"- Eventos recentes: {', '.join([e.get('label', 'unknown') for e in events])}"
        )
        return context
    
    def normalize_history(self, history: List[Dict]) -> List[Dict]:
        """Normalizar histórico de conversa"""
        if not history:
            return []
        
        # Limitar ao máximo de mensagens
        limited = history[-self.max_history:]
        return limited
    
    def build_agent_messages(self, question: str, history: List[Dict], events: List[Dict]) -> List[Dict]:
        """Montar sequência de mensagens para o modelo"""
        messages = [
            {"role": "system", "content": self.build_system_prompt()},
            {"role": "system", "content": self.build_event_context(events)},
        ]
        
        # Adicionar histórico normalizado
        messages.extend(self.normalize_history(history))
        
        # Adicionar pergunta atual
        messages.append({"role": "user", "content": question})
        
        return messages
    
    def get_status(self, events: List[Dict]) -> Dict:
        """Obter status do agente"""
        return {
            "name": self.profile.name,
            "role": self.profile.role,
            "goal": self.profile.goal,
            "events_in_context": len(events),
            "context_preview": self.build_event_context(events)[:200] + "..."
        }

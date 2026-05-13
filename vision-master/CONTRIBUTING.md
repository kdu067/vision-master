# 🤝 Como Contribuir - AgroVision AI

Obrigado por querer contribuir com AgroVision AI! Este documento descreve como participar do projeto.

---

## 📋 Código de Conduta

Somos compromissados com tornar este projeto inclusivo e respeitoso. Esperamos que todos os colaboradores:

- Sejam respeitosos nas comunicações
- Aceitem críticas construtivas
- Focarem no que é melhor para a comunidade
- Mostrem empatia com outros colaboradores

---

## 🚀 Como Começar

### 1. Fork o Repositório

```bash
# Clicar em "Fork" no GitHub
# Depois clonar localmente
git clone https://github.com/seu-usuario/agrovision_ai.git
cd agrovision_ia
```

### 2. Criar Branch para Sua Feature

```bash
git checkout -b feature/minha-feature
# ou para bugfix
git checkout -b fix/meu-bug
```

### 3. Fazer Mudanças

```bash
# Editar arquivos
# Testar localmente
# Commit com mensagens claras
git add .
git commit -m "feat: adicionar nova funcionalidade"
```

### 4. Push e Pull Request

```bash
git push origin feature/minha-feature
# Depois abrir PR no GitHub
```

---

## 🎯 Tipos de Contribuição

### 🐛 Reportar Bugs

Abra uma issue com:
- Descrição clara do problema
- Passos para reproduzir
- Versão do Python/Ollama/YOLO
- Logs de erro (se houver)

**Template:**
```markdown
## Descrição
[Descreva o bug de forma clara e concisa]

## Passos para Reproduzir
1. [Primeiro passo]
2. [Segundo passo]
...

## Comportamento Esperado
[O que deveria acontecer]

## Comportamento Atual
[O que realmente acontece]

## Sistema
- SO: Windows 11
- Python: 3.11.15
- Ollama: 0.20.7

## Logs/Screenshots
[Adicione logs ou prints]
```

### 💡 Sugerir Melhorias

Abra uma issue com:
- Descrição clara da melhoria
- Caso de uso
- Possível implementação (opcional)

**Template:**
```markdown
## Descrição da Melhoria
[Descreva a melhoria proposta]

## Caso de Uso
[Por que isso seria útil?]

## Solução Proposta
[Como poderia ser implementado? (opcional)]

## Alternativas Consideradas
[Outras abordagens? (opcional)]
```

### 📚 Melhorar Documentação

- Corrigir typos
- Melhorar clareza
- Adicionar exemplos
- Traduzir para outros idiomas

Edite os arquivos `.md` diretamente.

### ✨ Adicionar Features

1. Abrir issue descrevendo a feature
2. Aguardar feedback dos maintainers
3. Implementar em branch separado
4. Incluir testes
5. Abrir PR com documentação

---

## 💻 Desenvolvimento

### Estrutura do Código

```
agrovision_ia/
├── app.py                    # FastAPI principal
├── services/                 # Lógica de negócio
│   ├── config.py
│   ├── schemas.py
│   ├── event_repository.py
│   ├── ollama_client.py
│   ├── monitoring_agent.py
│   └── video_monitor.py
├── templates/               # HTML
├── static/                  # CSS/JS
└── test_services.py         # Testes
```

### Padrões de Código

**Python:**
```python
# Type hints
def get_events(limit: int = 12) -> List[Dict]:
    """Docstring em português."""
    pass

# Trailing comma
data = [
    "item1",
    "item2",
    "item3",
]

# F-strings
message = f"Erro: {error_code}"
```

**Commits:**
```
feat: adicionar autenticação
fix: corrigir bug no YOLO
docs: atualizar README
refactor: reorganizar services
test: adicionar testes unitários
chore: atualizar dependências
```

### Rodando Testes

```bash
# Instalar pytest
pip install pytest

# Rodar todos os testes
pytest

# Rodar arquivo específico
pytest test_services.py

# Rodar com cobertura
pip install pytest-cov
pytest --cov=services
```

### Verificar Qualidade

```bash
# Linting
pip install flake8
flake8 services/ app.py

# Type checking
pip install mypy
mypy services/

# Formatação
pip install black
black services/ app.py --check
```

---

## 🧪 Adicionando Testes

### Padrão de Teste

```python
import pytest
from services.event_repository import EventRepository

class TestEventRepository:
    """Testes para EventRepository"""
    
    @pytest.fixture
    def repo(self):
        """Setup para cada teste"""
        return EventRepository()
    
    def test_save_event(self, repo):
        """Testa salvamento de evento"""
        event_id = repo.save_event("car", 0.95)
        assert event_id > 0
        
    def test_get_recent_events(self, repo):
        """Testa leitura de eventos"""
        repo.save_event("car", 0.95)
        events = repo.get_recent_events()
        assert len(events) >= 1
```

### Executar Testes

```bash
# Tudo
pytest

# Apenas unit tests
pytest -m unit

# Apenas integration tests
pytest -m integration

# Com output verbose
pytest -v

# Parar no primeiro erro
pytest -x
```

---

## 📝 Documentação

### Adicionar Função

```python
def minha_funcao(param1: str, param2: int) -> bool:
    """
    Descrição breve em uma linha.
    
    Descrição detalhada em múltiplas linhas se necessário.
    Explique o que a função faz e por quê.
    
    Args:
        param1: Descrição do parâmetro 1
        param2: Descrição do parâmetro 2
    
    Returns:
        Descrição do retorno
    
    Raises:
        ValueError: Quando algo está errado
    
    Example:
        >>> minha_funcao("test", 42)
        True
    """
    pass
```

### Atualizar README

- Manter simples e claro
- Adicionar exemplos
- Incluir badges (status, versão, etc)
- Links relevantes

---

## 🔄 Processo de Pull Request

### Antes de Abrir PR

- [ ] Código formatado corretamente
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] Commits com mensagens claras
- [ ] Sem conflitos com main

### Descrição do PR

```markdown
## Descrição
[Explique as mudanças]

## Type de Mudança
- [ ] Bug fix
- [ ] Nova feature
- [ ] Breaking change
- [ ] Documentação

## Como Testar
1. [Passo 1]
2. [Passo 2]

## Checklist
- [ ] Código segue padrões do projeto
- [ ] Testes passam
- [ ] Documentação atualizada
- [ ] Sem warnings
```

### Depois de Abrir PR

- Responder feedback rapidamente
- Fazer ajustes solicitados
- Manter conversação profissional
- Atualizar branch se necessário

---

## 🏆 Reconhecimento

Contribuidores significativos serão:
- Mencionados em CONTRIBUTORS.md
- Adicionados como colaboradores
- Receber token de agradecimento

---

## 📞 Suporte

Dúvidas? Entre em contato:

- **Issues**: Para bugs e features
- **Discussions**: Para perguntas gerais
- **Email**: seu-email@example.com

---

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto.

---

Obrigado por contribuir! 🎉


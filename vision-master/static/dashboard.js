// Variáveis globais
const API_BASE = "";
let chatHistory = [];

// Inicializar na carga da página
document.addEventListener("DOMContentLoaded", () => {
    initializeDashboard();
    setupEventListeners();
    updateData();
    setInterval(updateData, 5000); // Atualizar a cada 5 segundos
});

function setupEventListeners() {
    const form = document.getElementById("chat-form");
    form.addEventListener("submit", handleChatSubmit);

    const textarea = document.getElementById("question-input");
    textarea.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && e.ctrlKey) {
            handleChatSubmit(e);
        }
    });
}

async function initializeDashboard() {
    console.log("Inicializando AgroVision AI Dashboard");
    
    // Carregar eventos iniciais
    await loadEvents();
    
    // Carregar status do agente
    await loadAgentStatus();
}

async function updateData() {
    await updateCameraStatus();
    await loadEvents();
    await loadAgentStatus();
}

// ============= CÂMERA =============

async function updateCameraStatus() {
    try {
        const response = await fetch(`${API_BASE}/camera/status`);
        const status = await response.json();
        
        const statusDiv = document.getElementById("camera-status");
        const onlineClass = status.online ? "online" : "offline";
        const onlineText = status.online ? "🟢 Online" : "🔴 Offline";
        
        statusDiv.className = `status ${onlineClass}`;
        statusDiv.innerHTML = `
            <strong>${onlineText}</strong><br>
            Tipo: ${status.source_type}<br>
            Frame disponível: ${status.has_live_frame ? "Sim" : "Não"}
        `;
    } catch (error) {
        console.error("Erro ao buscar status da câmera:", error);
    }
}

// ============= EVENTOS =============

async function loadEvents() {
    try {
        const response = await fetch(`${API_BASE}/events?limit=12`);
        const events = await response.json();
        
        const eventsList = document.getElementById("events-list");
        
        if (!events || events.length === 0) {
            eventsList.innerHTML = '<p>Nenhum evento registrado</p>';
            return;
        }
        
        eventsList.innerHTML = events.map(event => `
            <div class="event-item">
                <div>
                    <span class="event-label">${event.label}</span><br>
                    <span class="event-time">${event.event_time}</span>
                </div>
                <span class="event-confidence">${(event.confidence * 100).toFixed(1)}%</span>
            </div>
        `).join("");
    } catch (error) {
        console.error("Erro ao carregar eventos:", error);
    }
}

// ============= AGENTE =============

async function loadAgentStatus() {
    try {
        const response = await fetch(`${API_BASE}/agent/status`);
        const status = await response.json();
        
        const statusDiv = document.getElementById("agent-status");
        statusDiv.innerHTML = `
            <strong>${status.name}</strong><br>
            <em>${status.role}</em><br>
            Objetivo: ${status.goal}<br>
            <strong>Eventos em contexto: ${status.events_in_context}</strong><br>
            <details style="margin-top: 10px; font-size: 0.9em;">
                <summary>Ver contexto</summary>
                <pre style="background: #fff; padding: 10px; margin-top: 5px; border-radius: 4px; overflow-x: auto;">${status.context_preview}</pre>
            </details>
        `;
    } catch (error) {
        console.error("Erro ao carregar status do agente:", error);
    }
}

// ============= CHAT =============

async function handleChatSubmit(e) {
    e.preventDefault();
    
    const input = document.getElementById("question-input");
    const question = input.value.trim();
    
    if (!question) return;
    
    // Adicionar pergunta do usuário ao chat
    addMessageToChat(question, "user");
    input.value = "";
    
    // Desabilitar botão
    const button = document.querySelector(".chat-form button");
    button.disabled = true;
    
    // Adicionar pergunta ao histórico
    chatHistory.push({ role: "user", content: question });
    
    try {
        // Enviar para agente em streaming
        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question: question,
                history: chatHistory
            })
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let agentResponse = "";
        
        // Adicionar mensagem do agente em construção
        const messageIndex = addMessageToChat("", "agent");
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const text = decoder.decode(value);
            const lines = text.split("\n");
            
            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const content = line.slice(6);
                    
                    if (content === "[DONE]") {
                        continue;
                    }
                    
                    agentResponse += content;
                    updateMessageAtIndex(messageIndex, agentResponse);
                }
            }
        }
        
        // Adicionar resposta ao histórico
        chatHistory.push({ role: "assistant", content: agentResponse });
        
    } catch (error) {
        addMessageToChat(`Erro: ${error.message}`, "agent");
        console.error("Erro ao enviar pergunta:", error);
    } finally {
        button.disabled = false;
    }
}

function addMessageToChat(message, role) {
    const chatMessages = document.getElementById("chat-messages");
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${role}`;
    messageDiv.innerHTML = `<strong>${role === "user" ? "Você" : "Agente"}:</strong> <span>${escapeHtml(message)}</span>`;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return chatMessages.children.length - 1;
}

function updateMessageAtIndex(index, content) {
    const chatMessages = document.getElementById("chat-messages");
    const messageDiv = chatMessages.children[index];
    if (messageDiv) {
        const span = messageDiv.querySelector("span");
        if (span) {
            span.textContent = content;
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

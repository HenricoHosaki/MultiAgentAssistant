import { useState, useRef, useEffect } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesRef = useRef(null);

  useEffect(() => {
    const el = messagesRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, loading]);

  async function sendQuestion() {
    if (!question.trim() || loading) return;

    const history = messages.map((m) => ({ role: m.role, text: m.text }));
    const userMessage = { role: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage.text, history }),
      });
      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer,
          intent: data.intent,
          source: data.source,
          ticketId: data.ticket_id,
          tokenUsage: data.token_usage,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Erro ao conectar com o servidor." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function newConversation() {
    setMessages([]);
    setQuestion("");
  }

  function handleKeyDown(event) {
    if (event.key === "Enter") sendQuestion();
  }

  return (
    <div className="app">
      <div className="chat-card">
        <header className="chat-header">
          <div className="brand">
            <div className="brand-logo">💬</div>
            <div>
              <h1>Aria</h1>
              <p className="subtitle">Assistente de atendimento · produtos, entregas e pagamentos</p>
            </div>
          </div>
          <button
            className="new-chat-btn"
            onClick={newConversation}
            disabled={messages.length === 0 || loading}
          >
            Nova conversa
          </button>
        </header>

        <div className="messages" ref={messagesRef}>
          {messages.length === 0 && !loading && (
            <div className="empty-state">
              Olá! 👋 Sou a Aria.
              <br />
              Pergunte sobre produtos, entregas ou pagamentos.
            </div>
          )}

          {messages.map((message, index) => (
            <div key={index} className={`message-group ${message.role}`}>
              {message.role === "assistant" && message.source && (
                <div className="message-row assistant source-row">
                  <div className="avatar-spacer" />
                  <div className="source-chip">
                    {message.source.endsWith(".md")
                      ? `Leu ${message.source}`
                      : `Consultei ${message.source}`}
                  </div>
                </div>
              )}
              <div className={`message-row ${message.role}`}>
                {message.role === "assistant" && <div className="avatar">🤖</div>}
                <div className="message-bubble">
                  <p>{message.text}</p>
                </div>
              </div>
              {message.role === "assistant" && message.ticketId && (
                <div className="message-row assistant ticket-row">
                  <div className="avatar-spacer" />
                  <div className="ticket-chip">
                    🎫 Chamado aberto: #{message.ticketId}
                  </div>
                </div>
              )}
              {message.role === "assistant" && message.tokenUsage && (
                <div className="message-row assistant token-usage-row">
                  <div className="avatar-spacer" />
                  <div className="token-usage-chip">
                    {message.tokenUsage.total_tokens} tokens (
                    {message.tokenUsage.prompt_tokens} prompt +{" "}
                    {message.tokenUsage.completion_tokens} completion)
                  </div>
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="message-group assistant">
              <div className="message-row assistant">
                <div className="avatar">🤖</div>
                <div className="message-bubble">
                  <span className="typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="input-row">
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Digite sua pergunta..."
          />
          <button onClick={sendQuestion} disabled={loading || !question.trim()}>
            Enviar
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;

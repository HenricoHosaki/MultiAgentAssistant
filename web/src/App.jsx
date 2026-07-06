import { useState, useRef, useEffect } from "react";
import "./App.css";

const STRINGS = {
  en: {
    subtitle: "Customer support assistant · products, deliveries, and payments",
    newConversation: "New conversation",
    greeting: "Hi! 👋 I'm Aria.",
    greetingSub: "Ask me about products, deliveries, or payments.",
    placeholder: "Type your question...",
    send: "Send",
    cancel: "Cancel",
    connectionError: "Couldn't connect to the server. Please try again.",
    switchTo: "PT",
  },
  pt: {
    subtitle: "Assistente de atendimento · produtos, entregas e pagamentos",
    newConversation: "Nova conversa",
    greeting: "Oi! 👋 Sou a Aria.",
    greetingSub: "Pergunte sobre produtos, entregas ou pagamentos.",
    placeholder: "Digite sua pergunta...",
    send: "Enviar",
    cancel: "Cancelar",
    connectionError: "Não consegui conectar com o servidor. Tente novamente.",
    switchTo: "EN",
  },
};

const SUGGESTED_QUESTIONS = {
  en: [
    "I'd like to know more about product usage and care",
    "How does delivery work, and how long does it take?",
    "Do you have a loyalty rewards program?",
    "How can you help me?",
    "What can you do?",
  ],
  pt: [
    "Quero saber mais sobre uso e cuidados dos produtos",
    "Como funcionam as entregas e qual o prazo?",
    "Vocês têm programa de fidelidade com pontos?",
    "Como você pode me ajudar?",
    "O que vc consegue fazer?",
  ],
};

function App() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [uiLanguage, setUiLanguage] = useState("en");
  const messagesRef = useRef(null);
  const abortControllerRef = useRef(null);

  const t = STRINGS[uiLanguage];

  useEffect(() => {
    const el = messagesRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages, loading]);

  async function sendQuestion(overrideText) {
    const text = overrideText ?? question;
    if (!text.trim() || loading) return;

    const history = messages.map((m) => ({ role: m.role, text: m.text }));
    const userMessage = { role: "user", text };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    const controller = new AbortController();
    abortControllerRef.current = controller;
    const startTime = performance.now();

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage.text, history }),
        signal: controller.signal,
      });
      const data = await response.json();
      const elapsedSeconds = (performance.now() - startTime) / 1000;
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer,
          intent: data.intent,
          source: data.source,
          ticketId: data.ticket_id,
          language: data.language,
          tokenUsage: data.token_usage,
          elapsedSeconds,
        },
      ]);
    } catch (error) {
      if (error.name === "AbortError") {
        return;
      }
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: t.connectionError },
      ]);
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  }

  function cancelQuestion() {
    abortControllerRef.current?.abort();
    setMessages((prev) => prev.slice(0, -1));
  }

  function newConversation() {
    setMessages([]);
    setQuestion("");
  }

  function toggleLanguage() {
    setUiLanguage((prev) => (prev === "en" ? "pt" : "en"));
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
              <p className="subtitle">{t.subtitle}</p>
            </div>
          </div>
          <div className="header-actions">
            <button className="lang-toggle-btn" onClick={toggleLanguage}>
              {t.switchTo}
            </button>
            <button
              className="new-chat-btn"
              onClick={newConversation}
              disabled={messages.length === 0 || loading}
            >
              {t.newConversation}
            </button>
          </div>
        </header>

        <div className="messages" ref={messagesRef}>
          {messages.length === 0 && !loading && (
            <div className="empty-state">
              {t.greeting}
              <br />
              {t.greetingSub}
              <div className="suggestion-chips">
                {SUGGESTED_QUESTIONS[uiLanguage].map((suggestion) => (
                  <button
                    key={suggestion}
                    className="suggestion-chip"
                    onClick={() => sendQuestion(suggestion)}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div key={index} className={`message-group ${message.role}`}>
              {message.role === "assistant" && message.source && (
                <div className="message-row assistant source-row">
                  <div className="avatar-spacer" />
                  <div className="source-chip">
                    {message.language === "pt"
                      ? message.source.endsWith(".md")
                        ? `Leu ${message.source}`
                        : `Consultei ${message.source}`
                      : message.source.endsWith(".md")
                      ? `Read ${message.source}`
                      : `Checked ${message.source}`}
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
                    {message.language === "pt"
                      ? `🎫 Chamado aberto: #${message.ticketId}`
                      : `🎫 Ticket opened: #${message.ticketId}`}
                  </div>
                </div>
              )}
              {message.role === "assistant" && message.tokenUsage && (
                <div className="message-row assistant token-usage-row">
                  <div className="avatar-spacer" />
                  <div className="token-usage-chip">
                    {typeof message.elapsedSeconds === "number" && (
                      <>⏱ {message.elapsedSeconds.toFixed(1)}s · </>
                    )}
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
            placeholder={t.placeholder}
            aria-label={t.placeholder}
            disabled={loading}
          />
          {loading ? (
            <button onClick={cancelQuestion} className="cancel-btn">
              {t.cancel}
            </button>
          ) : (
            <button onClick={() => sendQuestion()} disabled={!question.trim()}>
              {t.send}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

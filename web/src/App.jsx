import { useState } from "react";
import "./App.css";

function App() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  async function sendQuestion() {
    if (!question.trim()) return;

    const userMessage = { role: "user", text: question };
    setMessages((prev) => [...prev, userMessage]);
    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage.text }),
      });
      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer,
          intent: data.intent,
          source: data.source,
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

  function handleKeyDown(event) {
    if (event.key === "Enter") sendQuestion();
  }

  return (
    <div className="chat-container">
      <h1>SAC Assistant</h1>
      <div className="messages">
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
            {message.role === "assistant" && message.tokenUsage && (
              <div className="message-row assistant token-usage-row">
                <div className="avatar-spacer" />
                <div className="token-usage-chip">
                   {message.tokenUsage.total_tokens} tokens ({message.tokenUsage.prompt_tokens} prompt + {message.tokenUsage.completion_tokens} completion)
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
                <p>Digitando...</p>
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
        <button onClick={sendQuestion}>Enviar</button>
      </div>
    </div>
  );
}

export default App;
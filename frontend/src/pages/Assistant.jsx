import React, { useEffect, useRef, useState } from "react";
import * as assistantApi from "../api/assistant.js";
import ErrorBanner from "../components/ErrorBanner.jsx";
import ReactMarkdown from "react-markdown";

const RISK_STYLES = {
  low: "border-gray-200",
  medium: "border-amber-300 bg-amber-50",
  high: "border-red-300 bg-red-50",
};

function ChatBubble({ message }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className="prose prose-sm max-w-none">
        <ReactMarkdown>{message.text}</ReactMarkdown>
      </div>
    </div>
  );
}

function ProposedActionCard({ action, onConfirm, onCancel, busy }) {
  return (
    <div
      className={`rounded-2xl border-2 p-4 ${RISK_STYLES[action.risk_level] || RISK_STYLES.low}`}
    >
      <p className="text-xs font-bold uppercase tracking-wide text-gray-500 mb-1">
        {action.risk_level === "high"
          ? "Needs your confirmation"
          : "Please confirm"}
      </p>
      <p className="font-medium mb-3">{action.summary}</p>
      <div className="flex gap-3">
        <button
          type="button"
          disabled={busy}
          className="btn-secondary flex-1"
          onClick={onCancel}
        >
          Cancel
        </button>
        <button
          type="button"
          disabled={busy}
          className="btn-primary flex-1"
          onClick={onConfirm}
        >
          Confirm
        </button>
      </div>
    </div>
  );
}

export default function Assistant() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: 'Hi! You can tell me about a sale ("I sold 2 milk and 1 bread"), or ask things like "how much have I made today?".',
    },
  ]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState(null);
  const [pendingAction, setPendingAction] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [listening, setListening] = useState(false);
  const scrollRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, pendingAction]);

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      setListening(false);
    };
    recognition.onerror = () => setListening(false);
    recognition.onend = () => setListening(false);
    recognitionRef.current = recognition;
  }, []);

  const speak = (text) => {
    if (!window.speechSynthesis || !text) return;
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  const toggleListening = () => {
    if (!recognitionRef.current) {
      setError(
        "Voice input isn't supported in this browser. You can still type your message.",
      );
      return;
    }
    if (listening) {
      recognitionRef.current.stop();
      setListening(false);
    } else {
      recognitionRef.current.start();
      setListening(true);
    }
  };

  const send = async (text, voice = false) => {
    if (!text.trim()) return;
    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setBusy(true);
    setError("");
    try {
      const res = await assistantApi.sendAssistantMessage({
        message: text,
        conversation_id: conversationId,
        input_mode: voice ? "voice" : "text",
      });
      setConversationId(res.conversation_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: res.reply_text },
      ]);
      setPendingAction(res.proposed_action || null);
      if (voice) speak(res.speak_text || res.reply_text);
    } catch (err) {
      setError(err.message || "Something went wrong reaching the assistant.");
    } finally {
      setBusy(false);
    }
  };

  const handleConfirm = async (confirmed) => {
    if (!pendingAction) return;
    setBusy(true);
    try {
      const res = await assistantApi.sendAssistantMessage({
        message: confirmed ? "yes" : "no",
        conversation_id: conversationId,
        confirm_action_id: pendingAction.action_id,
        confirmed,
      });
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: res.reply_text },
      ]);
      setPendingAction(res.proposed_action || null);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto flex flex-col h-[calc(100vh-56px)] lg:h-screen p-4">
      <h1 className="text-2xl font-bold mb-3">Business Assistant</h1>
      <ErrorBanner message={error} onDismiss={() => setError("")} />
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {messages.map((m, i) => (
          <ChatBubble key={i} message={m} />
        ))}
        {pendingAction && (
          <ProposedActionCard
            action={pendingAction}
            busy={busy}
            onConfirm={() => handleConfirm(true)}
            onCancel={() => handleConfirm(false)}
          />
        )}
        <div ref={scrollRef} />
      </div>

      <form
        className="flex items-center gap-2 pt-3 border-t mt-3"
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
      >
        <button
          type="button"
          onClick={toggleListening}
          className={`h-12 w-12 flex-shrink-0 rounded-full flex items-center justify-center text-xl ${listening ? "bg-red-500 text-white animate-pulse" : "bg-gray-100"}`}
          aria-label={listening ? "Stop listening" : "Start voice input"}
        >
          🎤
        </button>
        <input
          className="input flex-1"
          placeholder="Type a message…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={busy}
        />
        <button
          type="submit"
          disabled={busy || !input.trim()}
          className="btn-primary"
        >
          Send
        </button>
      </form>
    </div>
  );
}

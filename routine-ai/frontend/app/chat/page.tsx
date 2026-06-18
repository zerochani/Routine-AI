"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const STORAGE_KEY = "chat_messages";
const INITIAL_MESSAGE: Message = {
  role: "assistant",
  content: "안녕하세요! 루틴을 추가하거나 삭제하려면 말씀해주세요.\n예: \"매일 아침 7시에 운동 30분 추가해줘\"",
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>(() => {
    if (typeof window === "undefined") return [INITIAL_MESSAGE];
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [INITIAL_MESSAGE];
    } catch {
      return [INITIAL_MESSAGE];
    }
  });
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  }, [messages]);

  const send = async () => {
    const text = input.trim();
    if (!text || streaming) return;

    const userMsg: Message = { role: "user", content: text };
    const history = [...messages, userMsg];
    setMessages(history);
    setInput("");
    setStreaming(true);

    const assistantMsg: Message = { role: "assistant", content: "" };
    setMessages([...history, assistantMsg]);

    const apiMessages = history.map((m) => ({ role: m.role, content: m.content }));

    try {
      const res = await fetch(`${BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: apiMessages }),
      });

      const reader = res.body!.getReader();
      const decoder = new TextDecoder();
      let fullText = "";
      let firstLine = true;
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const payload = line.slice(6).trim();
          if (payload === "[DONE]") continue;

          try {
            const data = JSON.parse(payload);
            if (data.delta) {
              fullText += data.delta;
              const newlineIdx = fullText.indexOf("\n");
              let displayText: string;
              if (newlineIdx === -1) {
                // 첫 줄 완성 전: JSON이면 숨김
                try { JSON.parse(fullText.trim()); displayText = ""; }
                catch { displayText = fullText; }
              } else {
                // 첫 줄 완성: JSON이면 제거
                try { JSON.parse(fullText.slice(0, newlineIdx).trim()); displayText = fullText.slice(newlineIdx + 1); }
                catch { displayText = fullText; }
              }

              setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1] = { role: "assistant", content: displayText };
                return updated;
              });
            } else if (data.error) {
              setMessages((prev) => {
                const updated = [...prev];
                updated[updated.length - 1] = { role: "assistant", content: "오류가 발생했습니다. 잠시 후 다시 시도해주세요." };
                return updated;
              });
            }
          } catch {
            // ignore parse errors
          }
        }
      }
    } catch (e) {
      console.error(e);
      setMessages((prev) => {
        const updated = [...prev];
        updated[updated.length - 1] = { role: "assistant", content: "오류가 발생했습니다. 다시 시도해주세요." };
        return updated;
      });
    } finally {
      setStreaming(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <h1 className="text-xl font-bold mb-4">AI 채팅</h1>

      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-800 text-gray-100"
              }`}
            >
              {msg.content || (streaming && i === messages.length - 1 ? "..." : "")}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-2 pt-4 border-t border-gray-800">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
          placeholder="루틴을 추가하거나 삭제해보세요..."
          disabled={streaming}
          className="flex-1 rounded-xl bg-gray-800 border border-gray-700 px-4 py-3 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-blue-500 disabled:opacity-50"
        />
        <button
          onClick={send}
          disabled={streaming || !input.trim()}
          className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors"
        >
          전송
        </button>
      </div>
    </div>
  );
}

"use client";

import { useState, useRef, useEffect } from "react";
import type { AdvisorMessage } from "@/types/Explore";

interface ResearchAdvisorProps {
  isOpen: boolean;
  onClose: () => void;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "";

export default function ResearchAdvisor({ isOpen, onClose }: ResearchAdvisorProps) {
  const [messages, setMessages] = useState<AdvisorMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Hi! I'm your Research Advisor. Describe what you're working on or what problem you're trying to solve, and I'll help you find relevant papers and techniques.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: AdvisorMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(
        API_BASE ? `${API_BASE}/papers/contextual-search` : "/api/contextual-search",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            description: userMessage.content,
            fast_mode: false,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to get response");
      }

      const data = await response.json();

      const assistantMessage: AdvisorMessage = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.analysis || "I found some relevant papers for you.",
        papers: data.papers?.slice(0, 5).map((p: { id: string; title: string; summary?: string }) => ({
          id: p.id,
          title: p.title,
          summary: p.summary || "",
        })),
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      const errorMessage: AdvisorMessage = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: "Sorry, I encountered an error while searching. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onClose();
      }
    };
    document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  return (
    <div
      className={`advisor-overlay ${isOpen ? "advisor-overlay--open" : ""}`}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="advisor-panel">
        {/* Header */}
        <div className="advisor-header">
          <div className="advisor-header__title">
            <span className="advisor-header__icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
            </span>
            Research Advisor
          </div>
          <button className="advisor-close" onClick={onClose} aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className="advisor-messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`advisor-message advisor-message--${msg.role}`}>
              <div className="advisor-message__content">
                <p>{msg.content}</p>

                {/* Show paper recommendations */}
                {msg.papers && msg.papers.length > 0 && (
                  <div style={{ marginTop: "1rem" }}>
                    <p style={{ fontSize: "0.75rem", opacity: 0.7, marginBottom: "0.5rem" }}>
                      Relevant papers:
                    </p>
                    <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                      {msg.papers.map((paper, i) => (
                        <li
                          key={paper.id || i}
                          style={{
                            padding: "0.5rem",
                            marginBottom: "0.5rem",
                            background: "rgba(0,0,0,0.05)",
                            borderRadius: "0.5rem",
                          }}
                        >
                          <a
                            href={typeof paper.id === "string" && paper.id.startsWith("http") ? paper.id : `https://arxiv.org/abs/${paper.id}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              fontWeight: 500,
                              fontSize: "0.875rem",
                              display: "block",
                              marginBottom: "0.25rem",
                            }}
                          >
                            {paper.title}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="advisor-message advisor-message--assistant">
              <div className="advisor-message__content">
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <div className="spinner" style={{ width: 16, height: 16 }} />
                  <span>Searching papers...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="advisor-input-area">
          <form className="advisor-input-form" onSubmit={handleSubmit}>
            <input
              type="text"
              className="input advisor-input"
              placeholder="Describe your research problem..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
            />
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!input.trim() || isLoading}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

import { FormEvent, useEffect, useRef, useState } from "react";
import { chartFileUrl, getReport, postChat } from "../api/client";
import { ReportKind } from "../api/types";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  chartUrl?: string | null;
}

const CHIPS: { kind: ReportKind; label: string }[] = [
  { kind: "fitness", label: "🏥 Fitness & Injury Risk" },
  { kind: "top-performers", label: "⭐ Top Performers" },
  { kind: "financial", label: "💰 Financial Overview" },
];

let idCounter = 0;
function nextId(): string {
  idCounter += 1;
  return `msg-${idCounter}`;
}

export default function ChatPanel() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: nextId(),
      role: "assistant",
      text:
        "Ask me a tactical question, or tap a chip below for an instant, data-backed report - " +
        "those never need an LLM and always reflect the latest stats.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Found while verifying: without this, new chip/chat responses land
  // below the fold in the scrollable message list and the user has to
  // scroll down manually to see them.
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  const pushMessage = (msg: ChatMessage) => setMessages((prev) => [...prev, msg]);

  const handleChip = async (kind: ReportKind, label: string) => {
    setLoading(true);
    pushMessage({ id: nextId(), role: "user", text: label });
    try {
      const res = await getReport(kind);
      pushMessage({ id: nextId(), role: "assistant", text: res.text, chartUrl: res.chart_url });
    } catch (err) {
      pushMessage({
        id: nextId(),
        role: "assistant",
        text: `Couldn't load that report (${(err as Error).message}).`,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const message = input.trim();
    if (!message || loading) return;
    setInput("");
    setLoading(true);
    pushMessage({ id: nextId(), role: "user", text: message });
    try {
      const res = await postChat(message);
      pushMessage({ id: nextId(), role: "assistant", text: res.text, chartUrl: res.chart_url });
    } catch (err) {
      pushMessage({
        id: nextId(),
        role: "assistant",
        text: `Something went wrong (${(err as Error).message}).`,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div id="ask-the-analyst" className="w-80 shrink-0 border-l border-[#2a3344] bg-panel flex flex-col h-full">
      <div className="px-4 py-3 border-b border-[#2a3344]">
        <h2 className="font-medium">Ask the analyst</h2>
        <p className="text-textSecondary text-xs mt-0.5">Hybrid: instant chips, no LLM needed - or ask anything</p>
      </div>

      <div className="px-3 py-3 border-b border-[#2a3344] flex flex-wrap gap-2">
        {CHIPS.map((chip) => (
          <button
            key={chip.kind}
            onClick={() => handleChip(chip.kind, chip.label)}
            disabled={loading}
            className="text-xs px-2.5 py-1.5 rounded-full border border-indigo/40 bg-indigo/10 hover:bg-indigo/20 disabled:opacity-50 transition-colors"
          >
            {chip.label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-3">
        {messages.map((msg) => (
          <div key={msg.id} className={msg.role === "user" ? "flex justify-end" : "flex justify-start"}>
            <div
              className={`rounded-card px-3 py-2 max-w-[90%] text-sm whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-indigo/20 border border-indigo/40"
                  : "bg-card border border-[#2a3344]"
              }`}
            >
              {msg.text}
              {msg.chartUrl && (
                <img
                  src={chartFileUrl(msg.chartUrl)}
                  alt="Generated chart"
                  className="mt-2 rounded-card border border-[#2a3344] max-w-full"
                  // The scroll-to-bottom effect fires on message add, before
                  // this image has loaded and grown the container - re-scroll
                  // once it actually has a height, or the anchor undershoots.
                  onLoad={() => scrollRef.current?.scrollIntoView({ block: "end" })}
                />
              )}
            </div>
          </div>
        ))}
        {loading && <div className="text-textSecondary text-xs px-1">Thinking…</div>}
        <div ref={scrollRef} />
      </div>

      <form onSubmit={handleSubmit} className="border-t border-[#2a3344] p-3 flex gap-2">
        <input
          id="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about tactics, players…"
          className="flex-1 bg-card border border-[#2a3344] rounded-card px-3 py-2 text-sm text-textPrimary placeholder:text-textSecondary focus:outline-none focus:border-indigo"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="px-3 py-2 rounded-card bg-indigo text-white text-sm disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}

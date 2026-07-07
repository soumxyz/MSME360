import { useState, useEffect, useRef } from "react";
import {
  Send,
  X,
  Bot,
  User,
  ShieldCheck,
  Sparkles,
  ArrowRight,
  Info,
  Mic,
  MicOff,
  Volume2
} from "lucide-react";
import type { BusinessDetail } from "../lib/api/types";
import { cn } from "../lib/cn";
import { addAuditEvent } from "../lib/audit";
import { queryCopilot } from "../lib/api";

interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
  business: BusinessDetail;
  onDraftMemo: () => void;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  isDecline?: boolean;
  factors?: string[];
}

export function ChatPanel({ isOpen, onClose, business, onDraftMemo }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    if (messages.length === 0 && business) {
      setMessages([
        {
          id: `msg-welcome-${Date.now()}`,
          role: "assistant",
          content: `Hi! I'm your Credit Copilot. Ask me details about ${business.profile.name}'s risk factors, liquidity, or gst records. I'm strictly grounded to their scores and financial indicators.`,
        },
      ]);
    }
  }, [business, messages.length]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  if (!isOpen) return null;

  const startSpeechToText = () => {
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }
    const rec = new SpeechRecognition();
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = "en-IN"; // English (India)
    
    rec.onstart = () => setIsListening(true);
    rec.onend = () => setIsListening(false);
    rec.onerror = () => setIsListening(false);
    rec.onresult = (event: any) => {
      const text = event.results[0][0].transcript;
      setInput(text);
    };
    recognitionRef.current = rec;
    rec.start();
  };

  const stopSpeechToText = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopSpeechToText();
    } else {
      startSpeechToText();
    }
  };

  const speakText = (text: string) => {
    if (!window.speechSynthesis) {
      alert("Speech synthesis is not supported in this browser.");
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  };

  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    const userMsg: Message = {
      id: `msg-user-${Date.now()}`,
      role: "user",
      content: text,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    addAuditEvent({
      type: "copilot",
      business_id: business.business_id,
      business_name: business.profile.name,
      summary: `Copilot query: "${text.slice(0, 50)}${text.length > 50 ? "..." : ""}"`,
    });

    try {
      const response = await queryCopilot(business.business_id, text);
      const reply = response.answer;
      const lowerReply = reply.toLowerCase();
      const isDecline = lowerReply.includes("cannot answer") || lowerReply.includes("out of scope") || lowerReply.includes("out-of-scope");
      
      const referencedFactors = business.factors
        .filter((f) => lowerReply.includes(f.label.toLowerCase()) || lowerReply.includes(f.name.toLowerCase()))
        .map((f) => f.label);

      if (lowerReply.includes("credit memo") || lowerReply.includes("draft memo")) {
        setTimeout(() => onDraftMemo(), 1200);
      }

      setMessages((prev) => [
        ...prev,
        {
          id: `msg-copilot-${Date.now()}`,
          role: "assistant",
          content: reply,
          isDecline,
          factors: referencedFactors,
        },
      ]);
    } catch (e: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `msg-error-${Date.now()}`,
          role: "assistant",
          content: "Error: Failed to fetch grounded response from Credit Copilot.",
          isDecline: true,
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const suggestions = [
    { label: "Why is the score?", q: `Why is the score ${business.score.score}?` },
    { label: "What loan size is safe?", q: "What loan size is safe?" },
    { label: "Draft credit memo", q: "Draft the credit memo" },
    { label: "Out-of-Scope test", q: "Out-of-Scope: Predict their stock price next week" },
  ];

  return (
    <div className="fixed inset-y-0 right-0 z-50 flex w-full max-w-[420px] flex-col border-l border-border bg-white shadow-2xl transition-transform duration-300">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border px-4 py-3.5 bg-[#fafafa]">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-primary" aria-hidden />
          <div>
            <h2 className="text-sm font-semibold text-text-primary">Credit Copilot</h2>
            <p className="text-[10px] font-semibold text-[#008269] flex items-center gap-1">
              <ShieldCheck className="w-3 h-3 text-success" /> Grounded Scored Factors
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="rounded-lg p-1.5 text-text-secondary hover:bg-background-muted hover:text-text-primary"
          aria-label="Close Copilot Panel"
        >
          <X className="w-4.5 h-4.5" />
        </button>
      </div>

      {/* Grounding Warning */}
      <div className="flex items-start gap-2 bg-[#008269]/5 px-4 py-2 text-[11px] text-[#008269] border-b border-[#008269]/10">
        <Info className="w-3.5 h-3.5 shrink-0 mt-0.5" />
        <p>
          <strong>Anti-Hallucination Discipline:</strong> Answers are restricted to factors generated from verified bank statements and GST filings.
        </p>
      </div>

      {/* Chat Thread */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m) => (
          <div
            key={m.id}
            className={cn(
              "flex gap-3 max-w-[85%]",
              m.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
            )}
          >
            {/* Avatar */}
            <div
              className={cn(
                "flex w-7 h-7 shrink-0 items-center justify-center rounded-full text-xs",
                m.role === "user"
                  ? "bg-background-muted text-text-primary"
                  : "bg-primary/10 text-primary font-semibold"
              )}
            >
              {m.role === "user" ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
            </div>

            {/* Bubble */}
            <div
              className={cn(
                "rounded-lg p-3 text-xs leading-relaxed position-relative",
                m.role === "user"
                  ? "bg-primary text-white rounded-tr-none"
                  : m.isDecline
                  ? "bg-red-50 text-error border border-red-200 rounded-tl-none"
                  : "bg-background-muted/80 text-text-primary rounded-tl-none"
              )}
            >
              <div className="flex justify-between items-start gap-2">
                <div className="flex-1">
                  {m.content.split("\n\n").map((para, i) => (
                    <p key={i} className={i > 0 ? "mt-2" : ""}>
                      {para}
                    </p>
                  ))}
                </div>
                {m.role === "assistant" && (
                  <button
                    onClick={() => speakText(m.content)}
                    className="p-1 rounded text-text-secondary hover:text-[#008269] hover:bg-white/50 transition-colors cursor-pointer shrink-0"
                    title="Read Aloud"
                  >
                    <Volume2 className="w-3.5 h-3.5" />
                  </button>
                )}
              </div>

              {m.factors && m.factors.length > 0 && (
                <div className="mt-2.5 flex flex-wrap gap-1">
                  {m.factors.map((f) => (
                    <span
                      key={f}
                      className="inline-block rounded bg-primary/10 px-1.5 py-0.5 text-[9px] font-semibold text-primary border border-primary/10"
                    >
                      Ref: {f}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex gap-3 mr-auto max-w-[85%]">
            <div className="flex w-7 h-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Bot className="w-3.5 h-3.5" />
            </div>
            <div className="rounded-lg bg-background-muted/80 p-3 rounded-tl-none">
              <div className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 animate-bounce rounded-full bg-text-secondary" />
                <span className="w-1.5 h-1.5 animate-bounce rounded-full bg-text-secondary delay-150" />
                <span className="w-1.5 h-1.5 animate-bounce rounded-full bg-text-secondary delay-300" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Suggested chips */}
      <div className="border-t border-border px-4 py-2.5 bg-background-muted/30 space-y-1.5">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-text-secondary">Suggested Questions</p>
        <div className="flex flex-wrap gap-1.5">
          {suggestions.map((s) => (
            <button
              key={s.label}
              onClick={() => handleSend(s.q)}
              disabled={isTyping}
              className="inline-flex cursor-pointer items-center gap-1 rounded-full border border-border bg-white px-2.5 py-1 text-[10px] font-medium text-text-primary transition-colors hover:bg-background-muted hover:text-primary disabled:opacity-50"
            >
              <Sparkles className="w-3 h-3 text-primary shrink-0" />
              {s.label}
              <ArrowRight className="w-2.5 h-2.5 text-text-secondary shrink-0" />
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend(input);
        }}
        className="flex items-center gap-2 border-t border-border bg-white p-3"
      >
        <button
          type="button"
          onClick={toggleListening}
          className={cn(
            "w-8 h-8 flex items-center justify-center rounded border transition-colors cursor-pointer",
            isListening
              ? "bg-error/15 border-error text-error animate-pulse"
              : "bg-background-muted border-border text-text-secondary hover:text-[#008269]"
          )}
          title={isListening ? "Listening... Click to stop" : "Start Voice Query"}
        >
          {isListening ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
        </button>

        <input
          type="text"
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isTyping}
          className="flex-1 rounded-md border border-border px-3 py-2 text-xs text-text-primary placeholder:text-text-secondary/70 focus:border-primary focus:outline-none"
        />
        
        <button
          type="submit"
          className="w-8 h-8 p-0 flex items-center justify-center rounded bg-primary hover:bg-primary-hover text-white disabled:opacity-50 cursor-pointer transition-colors"
          disabled={!input.trim() || isTyping}
        >
          <Send className="w-3.5 h-3.5" />
        </button>
      </form>
    </div>
  );
}

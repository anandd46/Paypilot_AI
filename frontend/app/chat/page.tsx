"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Bot, Send, ShoppingCart, Plus, Minus, Star, Loader2,
  Package, Sparkles, ArrowRight, X, ExternalLink, Zap,
  TrendingUp, Info, Smartphone, Laptop, Headphones, Camera,
  Watch, Tablet, Speaker, Gamepad2, Box, Mouse,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import api, { type ChatResponse, type Product, type Cart } from "@/lib/api";
import Link from "next/link";
import Image from "next/image";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  intent?: string;
  confidence?: string;
  products?: Product[];
  suggested_prompts?: string[];
  is_demo?: boolean;
  provider?: string;
  timestamp: Date;
}

function ProductCard({ product, onAddToCart }: { product: Product; onAddToCart: (id: string) => void }) {
  const [adding, setAdding] = useState(false);
  const [imgError, setImgError] = useState(false);

  const getCategoryIcon = (cat: string) => {
    const c = cat?.toLowerCase() ?? "";
    const cls = "w-7 h-7 opacity-70";
    if (c.includes("smartphone") || c.includes("phone")) return <Smartphone className={cls} />;
    if (c.includes("laptop")) return <Laptop className={cls} />;
    if (c.includes("headphone") || c.includes("earbud")) return <Headphones className={cls} />;
    if (c.includes("camera")) return <Camera className={cls} />;
    if (c.includes("watch")) return <Watch className={cls} />;
    if (c.includes("tablet")) return <Tablet className={cls} />;
    if (c.includes("speaker")) return <Speaker className={cls} />;
    if (c.includes("gaming")) return <Gamepad2 className={cls} />;
    if (c.includes("access")) return <Mouse className={cls} />;
    return <Box className={cls} />;
  };

  const getCategoryGradient = (cat: string) => {
    const c = cat?.toLowerCase() ?? "";
    if (c.includes("smartphone")) return "from-blue-600/40 to-cyan-500/30";
    if (c.includes("laptop")) return "from-violet-600/40 to-purple-500/30";
    if (c.includes("headphone") || c.includes("earbud")) return "from-rose-600/40 to-pink-500/30";
    if (c.includes("camera")) return "from-amber-600/40 to-yellow-500/30";
    if (c.includes("watch")) return "from-emerald-600/40 to-teal-500/30";
    if (c.includes("tablet")) return "from-sky-600/40 to-blue-500/30";
    if (c.includes("speaker")) return "from-orange-600/40 to-amber-500/30";
    if (c.includes("gaming")) return "from-green-600/40 to-lime-500/30";
    return "from-slate-600/40 to-zinc-500/30";
  };
  
  const handleAdd = async () => {
    setAdding(true);
    try {
      await onAddToCart(product.id);
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="glass rounded-xl p-4 border border-border hover:border-primary/40 transition-all hover:scale-[1.01] animate-fade-in">
      <div className="flex gap-3">
        {product.image_url && !imgError ? (
          <div className="w-16 h-16 rounded-lg overflow-hidden flex-shrink-0 bg-secondary">
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full h-full object-cover"
              onError={() => setImgError(true)}
            />
          </div>
        ) : (
          <div className={`w-16 h-16 rounded-lg flex items-center justify-center flex-shrink-0 bg-gradient-to-br ${getCategoryGradient(product.category)} text-foreground/60`}>
            {getCategoryIcon(product.category)}
          </div>
        )}
        <div className="flex-1 min-w-0">
          <h4 className="font-medium text-sm truncate">{product.name}</h4>
          <div className="flex items-center gap-1 mt-0.5">
            <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
            <span className="text-xs text-muted-foreground">{product.rating} ({product.review_count?.toLocaleString()})</span>
          </div>
          <div className="flex items-center gap-2 mt-1">
            <span className="font-bold text-primary">₹{product.price.toLocaleString()}</span>
            {product.original_price && product.original_price > product.price && (
              <span className="text-xs text-muted-foreground line-through">₹{product.original_price.toLocaleString()}</span>
            )}
            {product.discount_percent && (
              <span className="text-xs text-emerald-400">{product.discount_percent}% off</span>
            )}
          </div>
          <div className="flex items-center gap-2 mt-1">
            {product.brand && (
              <span className="text-xs bg-secondary px-2 py-0.5 rounded-full text-muted-foreground">{product.brand}</span>
            )}
            {product.stock < 5 && product.stock > 0 && (
              <span className="text-xs text-amber-400">Only {product.stock} left</span>
            )}
          </div>
        </div>
      </div>
      <button
        onClick={handleAdd}
        disabled={adding || product.stock === 0}
        className="mt-3 w-full flex items-center justify-center gap-2 bg-primary/10 hover:bg-primary/20 border border-primary/30 text-primary px-3 py-2 rounded-lg text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {adding ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <ShoppingCart className="w-4 h-4" />
        )}
        {product.stock === 0 ? "Out of Stock" : adding ? "Adding..." : "Add to Cart"}
      </button>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex items-end gap-2">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center flex-shrink-0">
        <Bot className="w-4 h-4 text-white" />
      </div>
      <div className="glass rounded-2xl rounded-bl-none px-4 py-3">
        <div className="flex gap-1 items-center h-4">
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
        </div>
      </div>
    </div>
  );
}

const STARTER_PROMPTS = [
  "Find gaming headphones under ₹5,000",
  "Recommend a laptop for programming",
  "Show me flagship smartphones",
  "What's in my cart?",
  "Compare Sony and Bose headphones",
  "Best cameras for beginners under ₹70,000",
];

export default function ChatPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [cartCount, setCartCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login?redirect=/chat");
      return;
    }
    // Welcome message
    setMessages([{
      id: "welcome",
      role: "assistant",
      content: "Hello! I'm PayPilot AI, your intelligent shopping assistant. I can help you find products, compare options, manage your cart, and checkout — just tell me what you're looking for! 🛍️",
      suggested_prompts: STARTER_PROMPTS,
      timestamp: new Date(),
    }]);
    // Load cart count
    api.getCart().then(c => setCartCount(c.item_count)).catch(() => {});
  }, [isAuthenticated, router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text?: string) => {
    const message = text || input.trim();
    if (!message || loading) return;
    setInput("");

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: message,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await api.chat(message, sessionId);
      setSessionId(res.session_id);
      if (res.cart_updated) {
        api.getCart().then(c => setCartCount(c.item_count)).catch(() => {});
      }

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: res.message,
        intent: res.intent,
        confidence: res.confidence,
        products: res.products,
        suggested_prompts: res.suggested_prompts,
        is_demo: res.is_demo,
        provider: res.provider,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      setMessages(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I encountered an issue. Please ensure the backend is running and try again.",
        timestamp: new Date(),
      }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleAddToCart = async (productId: string) => {
    try {
      const cart = await api.addToCart(productId, 1);
      setCartCount(cart.item_count);
    } catch (err) {
      console.error("Failed to add to cart:", err);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="glass border-b border-border px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center">
              <Zap className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-bold gradient-text">PayPilot AI</span>
          </Link>
          <span className="text-muted-foreground text-sm hidden md:block">AI Assistant</span>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/shop" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Shop
          </Link>
          <Link href="/cart" className="relative flex items-center gap-2 glass px-3 py-2 rounded-lg text-sm hover:bg-card transition-colors">
            <ShoppingCart className="w-4 h-4" />
            {cartCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-primary text-primary-foreground text-xs rounded-full flex items-center justify-center">
                {cartCount}
              </span>
            )}
          </Link>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} gap-2 animate-fade-in`}>
            {msg.role === "assistant" && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center flex-shrink-0 mt-1">
                <Bot className="w-4 h-4 text-white" />
              </div>
            )}
            <div className={`max-w-[80%] flex flex-col gap-2 ${msg.role === "user" ? "items-end" : "items-start"}`}>
              <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-gradient-to-br from-cyan-500/20 to-violet-500/20 border border-primary/30 rounded-br-none"
                  : "glass rounded-bl-none"
              }`}>
                {msg.content}
                {msg.intent && (
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-xs px-2 py-0.5 rounded-full bg-secondary text-muted-foreground">
                      {msg.intent.replace("_", " ")}
                    </span>
                    {msg.confidence && (
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        msg.confidence === "HIGH" ? "text-emerald-400 bg-emerald-400/10" :
                        msg.confidence === "MEDIUM" ? "text-amber-400 bg-amber-400/10" :
                        "text-rose-400 bg-rose-400/10"
                      }`}>
                        {msg.confidence}
                      </span>
                    )}
                    {msg.provider && (
                      <span className="text-xs text-muted-foreground">via {msg.provider}</span>
                    )}
                  </div>
                )}
              </div>

              {/* Product grid */}
              {msg.products && msg.products.length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl">
                  {msg.products.slice(0, 4).map((p) => (
                    <ProductCard key={p.id} product={p} onAddToCart={handleAddToCart} />
                  ))}
                </div>
              )}

              {/* Suggested prompts */}
              {msg.suggested_prompts && msg.suggested_prompts.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {msg.suggested_prompts.map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => sendMessage(prompt)}
                      className="text-xs glass px-3 py-1.5 rounded-full hover:bg-primary/10 hover:text-primary hover:border-primary/30 border border-border transition-all"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              )}

              <span className="text-xs text-muted-foreground">
                {msg.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
          </div>
        ))}
        {loading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="glass border-t border-border p-4">
        <div className="max-w-4xl mx-auto flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me about products, your cart, or checkout..."
              className="w-full glass rounded-xl px-4 py-3 text-sm resize-none outline-none focus:border-primary/50 border border-border transition-colors min-h-[44px] max-h-[120px]"
              rows={1}
              id="chat-input"
            />
          </div>
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim() || loading}
            id="send-button"
            className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-violet-500 text-white px-4 py-3 rounded-xl font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </div>
  );
}

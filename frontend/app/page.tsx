"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Bot, ShoppingCart, TrendingUp, Zap, ChevronRight, Star,
  Shield, Brain, BarChart3, Sparkles, ArrowRight, Package,
  CreditCard, Activity,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import api from "@/lib/api";

interface HealthStatus {
  ai: string;
  payment: string;
  database: string;
  aiProvider: string;
  paymentProvider: string;
}

export default function HomePage() {
  const { isAuthenticated, user } = useAuth();
  const router = useRouter();
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    api.getHealth().then((h) => {
      setHealth({
        ai: h.ai?.status || "unknown",
        payment: h.payment?.status || "unknown",
        database: h.database?.status || "unknown",
        aiProvider: h.ai?.provider || "mock",
        paymentProvider: h.payment?.provider || "demo",
      });
    }).catch(() => {
      setHealth({
        ai: "demo_mode", payment: "demo_mode",
        database: "offline", aiProvider: "mock", paymentProvider: "demo",
      });
    });
  }, []);

  const features = [
    {
      icon: Brain,
      title: "AI Commerce Agent",
      description: "12-state explicit agent machine that understands intent, recommends products, and guides purchase — without hallucinating prices or inventory.",
      color: "from-blue-500/20 to-cyan-500/20",
      border: "border-blue-500/30",
    },
    {
      icon: ShoppingCart,
      title: "Agentic Checkout",
      description: "Inventory-safe atomic checkout with Razorpay integration. Agent confirms before any financial action — full policy validation.",
      color: "from-violet-500/20 to-purple-500/20",
      border: "border-violet-500/30",
    },
    {
      icon: TrendingUp,
      title: "Upsell & Cross-sell Engine",
      description: "Weighted scoring (intent 30% + semantic 25% + budget 20% + rating 15% + popularity 10%) — honest, data-driven recommendations.",
      color: "from-emerald-500/20 to-green-500/20",
      border: "border-emerald-500/30",
    },
    {
      icon: BarChart3,
      title: "Merchant Analytics",
      description: "Real-time revenue, AI-assisted conversion tracking, payment success rates, and per-category performance insights.",
      color: "from-orange-500/20 to-amber-500/20",
      border: "border-orange-500/30",
    },
    {
      icon: Shield,
      title: "Financial Safety",
      description: "PolicyValidator gates every AI action. LLM never writes to DB directly — all mutations via typed tool calls with explicit state machine.",
      color: "from-rose-500/20 to-red-500/20",
      border: "border-rose-500/30",
    },
    {
      icon: Activity,
      title: "Audit & Observability",
      description: "Every agent action logged with intent, tool calls, duration, confidence. No chain-of-thought stored — clean audit trail.",
      color: "from-sky-500/20 to-teal-500/20",
      border: "border-sky-500/30",
    },
  ];

  const stats = [
    { label: "Products Seeded", value: "50+" },
    { label: "Agent States", value: "12" },
    { label: "API Endpoints", value: "40+" },
    { label: "Categories", value: "9" },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation */}
      <nav className="glass sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-lg gradient-text">PayPilot AI</span>
          </div>
          <div className="flex items-center gap-4">
            {health && (
              <div className="hidden md:flex items-center gap-2">
                <span className={`text-xs px-2 py-1 rounded-full ${health.ai === "demo_mode" ? "status-demo" : "status-operational"}`}>
                  AI: {health.aiProvider}
                </span>
                <span className={`text-xs px-2 py-1 rounded-full ${health.payment === "demo_mode" ? "status-demo" : "status-operational"}`}>
                  Pay: {health.paymentProvider}
                </span>
              </div>
            )}
            {isAuthenticated ? (
              <div className="flex items-center gap-3">
                <Link
                  href="/shop"
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Shop
                </Link>
                <Link
                  href={user?.role === "customer" ? "/dashboard" : "/merchant"}
                  className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium hover:opacity-90 transition-opacity"
                >
                  Dashboard <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link href="/login" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                  Login
                </Link>
                <Link
                  href="/register"
                  className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-violet-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:opacity-90 transition-opacity"
                >
                  Get Started <ChevronRight className="w-3 h-3" />
                </Link>
              </div>
            )}
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative flex-1 flex flex-col items-center justify-center py-24 px-6 overflow-hidden">
        {/* Background glow */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
          <div className="absolute top-1/3 right-1/4 w-80 h-80 bg-violet-500/10 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 left-1/2 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl" />
        </div>

        <div className="relative text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full text-sm text-muted-foreground mb-8">
            <Sparkles className="w-3 h-3 text-cyan-400" />
            <span>Production-Ready AI Commerce Platform</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            Commerce that{" "}
            <span className="gradient-text">thinks</span>,<br />
            recommends, and{" "}
            <span className="gradient-text">converts.</span>
          </h1>

          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
            PayPilot AI is an agentic commerce platform that turns customer intent into personalized
            shopping experiences — with a 12-state agent machine, financial safety guardrails,
            and merchant growth analytics.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href={isAuthenticated ? "/chat" : "/register"}
              className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-violet-500 text-white px-8 py-4 rounded-xl text-lg font-medium hover:opacity-90 transition-all hover:scale-105 glow"
            >
              <Bot className="w-5 h-5" />
              Try AI Assistant
            </Link>
            <Link
              href="/shop"
              className="flex items-center gap-2 glass px-8 py-4 rounded-xl text-lg font-medium hover:bg-card transition-all"
            >
              <ShoppingCart className="w-5 h-5" />
              Browse Shop
            </Link>
          </div>
        </div>

        {/* Stats */}
        <div className="relative mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
          {stats.map((s) => (
            <div key={s.label} className="glass rounded-xl p-4 text-center">
              <div className="text-2xl font-bold gradient-text">{s.value}</div>
              <div className="text-xs text-muted-foreground mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Production-Grade Architecture
            </h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Every component built with financial safety, observability, and merchant ROI in mind.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f) => (
              <div
                key={f.title}
                className={`glass rounded-2xl p-6 border ${f.border} hover:scale-[1.02] transition-transform`}
              >
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${f.color} flex items-center justify-center mb-4 border ${f.border}`}>
                  <f.icon className="w-6 h-6" />
                </div>
                <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="glass rounded-3xl p-12 text-center gradient-border">
            <h2 className="text-3xl font-bold mb-4">Ready to experience agentic commerce?</h2>
            <p className="text-muted-foreground mb-8">
              Login with demo credentials or create an account to start shopping with AI guidance.
            </p>
            <div className="glass rounded-xl p-4 inline-block mb-8 text-left text-sm">
              <div className="text-muted-foreground mb-2 text-xs uppercase tracking-wider">Demo Credentials</div>
              <div className="space-y-1">
                <div><span className="text-muted-foreground">Customer:</span> <span className="text-foreground font-mono">customer@paypilot.demo / Demo@123</span></div>
                <div><span className="text-muted-foreground">Merchant:</span> <span className="text-foreground font-mono">merchant@paypilot.demo / Demo@123</span></div>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/login"
                className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-violet-500 text-white px-8 py-3 rounded-xl font-medium hover:opacity-90 transition-opacity"
              >
                Login with Demo Account <ArrowRight className="w-4 h-4" />
              </Link>
              <Link href="/shop" className="flex items-center gap-2 glass px-8 py-3 rounded-xl font-medium hover:bg-card transition-colors">
                Browse Products <Package className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="glass border-t border-border px-6 py-8">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center">
              <Zap className="w-3 h-3 text-white" />
            </div>
            <span className="font-bold gradient-text">PayPilot AI</span>
            <span className="text-muted-foreground text-sm">v1.0.0</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-muted-foreground">
            <Link href="/docs" className="hover:text-foreground transition-colors">Docs</Link>
            <Link href="/shop" className="hover:text-foreground transition-colors">Shop</Link>
            <Link href="/chat" className="hover:text-foreground transition-colors">AI Assistant</Link>
            <Link href="/merchant" className="hover:text-foreground transition-colors">Merchant</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

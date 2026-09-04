"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Zap, Eye, EyeOff, Loader2, Bot } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      const params = new URLSearchParams(window.location.search);
      router.push(params.get("redirect") || "/");
    } catch (err: unknown) {
      const e = err as { response?: { data?: { detail?: string } } };
      setError(e?.response?.data?.detail || "Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = (role: "customer" | "merchant") => {
    setEmail(`${role}@paypilot.demo`);
    setPassword("Demo@123");
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-violet-500/10 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-md relative">
        <div className="glass rounded-3xl p-8 border border-border animate-fade-in">
          {/* Header */}
          <div className="text-center mb-8">
            <Link href="/" className="inline-flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold gradient-text">PayPilot AI</span>
            </Link>
            <h1 className="text-2xl font-bold">Welcome back</h1>
            <p className="text-muted-foreground text-sm mt-1">Sign in to your account</p>
          </div>

          {/* Demo shortcuts */}
          <div className="glass rounded-xl p-3 mb-6 border border-border">
            <div className="text-xs text-muted-foreground mb-2 text-center">Quick Demo Access</div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => fillDemo("customer")}
                className="text-xs glass py-2 px-3 rounded-lg hover:bg-primary/10 hover:text-primary hover:border-primary/30 border border-border transition-all"
              >
                Customer Demo
              </button>
              <button
                type="button"
                onClick={() => fillDemo("merchant")}
                className="text-xs glass py-2 px-3 rounded-lg hover:bg-accent/10 hover:text-accent hover:border-accent/30 border border-border transition-all"
              >
                Merchant Demo
              </button>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="text-sm text-muted-foreground mb-1.5 block">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@example.com"
                className="w-full glass rounded-xl px-4 py-3 text-sm border border-border focus:border-primary/50 outline-none transition-colors"
              />
            </div>
            <div>
              <label htmlFor="password" className="text-sm text-muted-foreground mb-1.5 block">Password</label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full glass rounded-xl px-4 py-3 pr-10 text-sm border border-border focus:border-primary/50 outline-none transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="text-sm text-destructive bg-destructive/10 border border-destructive/20 px-4 py-2.5 rounded-xl">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              id="login-button"
              className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-cyan-500 to-violet-500 text-white px-6 py-3 rounded-xl font-medium hover:opacity-90 transition-all disabled:opacity-70"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <p className="text-center text-sm text-muted-foreground mt-6">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="text-primary hover:underline">Create one</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

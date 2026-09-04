"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Shield, Users, Activity, FileText, Zap, Loader2, Server, Database, Bot, CheckCircle2, XCircle } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import api, { type HealthResponse } from "@/lib/api";

export default function AdminDashboard() {
  const { isAuthenticated, isAdmin } = useAuth();
  const router = useRouter();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) { router.push("/login?redirect=/admin"); return; }
    if (!isAdmin) { router.push("/"); return; }
    loadHealth();
  }, [isAuthenticated, isAdmin]);

  const loadHealth = async () => {
    try {
      const data = await api.getHealth();
      setHealth(data);
    } catch (err) {
      console.error("Failed to load health");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;
  }

  const StatusIcon = ({ status }: { status: string }) => {
    return status === "ok" ? (
      <CheckCircle2 className="w-5 h-5 text-emerald-400" />
    ) : (
      <XCircle className="w-5 h-5 text-rose-400" />
    );
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="glass sticky top-0 z-50 border-b border-border px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center">
              <Zap className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-bold gradient-text">PayPilot AI Admin</span>
          </Link>
          <nav className="hidden md:flex items-center gap-4 text-sm">
            <Link href="/admin" className="text-primary font-medium">Dashboard</Link>
            <Link href="/merchant" className="text-muted-foreground hover:text-foreground">Merchant View</Link>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <h1 className="text-3xl font-bold mb-8 flex items-center gap-3">
          <Shield className="w-8 h-8 text-primary" /> System Admin
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12 animate-fade-in">
          {health && (
            <>
              <div className="glass rounded-2xl p-6 border border-border flex flex-col items-center text-center">
                <Server className="w-8 h-8 mb-4 text-cyan-400" />
                <h3 className="font-bold mb-2">API Server</h3>
                <div className="flex items-center gap-2 text-sm">
                  <StatusIcon status={health.api.status} /> {health.api.status.toUpperCase()}
                </div>
              </div>
              <div className="glass rounded-2xl p-6 border border-border flex flex-col items-center text-center">
                <Database className="w-8 h-8 mb-4 text-violet-400" />
                <h3 className="font-bold mb-2">Database</h3>
                <div className="flex items-center gap-2 text-sm">
                  <StatusIcon status={health.database.status} /> {health.database.status.toUpperCase()}
                </div>
              </div>
              <div className="glass rounded-2xl p-6 border border-border flex flex-col items-center text-center">
                <Bot className="w-8 h-8 mb-4 text-emerald-400" />
                <h3 className="font-bold mb-2">AI Provider</h3>
                <div className="flex flex-col items-center gap-1 text-sm">
                  <div className="flex items-center gap-2"><StatusIcon status={health.ai.status} /> {health.ai.status.toUpperCase()}</div>
                  <div className="text-xs text-muted-foreground capitalize">{health.ai.provider}</div>
                </div>
              </div>
              <div className="glass rounded-2xl p-6 border border-border flex flex-col items-center text-center">
                <Shield className="w-8 h-8 mb-4 text-amber-400" />
                <h3 className="font-bold mb-2">Payment Gateway</h3>
                <div className="flex flex-col items-center gap-1 text-sm">
                  <div className="flex items-center gap-2"><StatusIcon status={health.payment.status} /> {health.payment.status.toUpperCase()}</div>
                  <div className="text-xs text-muted-foreground capitalize">{health.payment.provider}</div>
                </div>
              </div>
            </>
          )}
        </div>

        <h2 className="text-2xl font-bold mb-6">Management Modules</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in" style={{ animationDelay: '100ms' }}>
          <Link href="/admin/users" className="glass rounded-2xl p-8 border border-border hover:border-primary/50 transition-colors group text-center">
            <Users className="w-12 h-12 text-muted-foreground mx-auto mb-4 group-hover:text-primary transition-colors" />
            <h3 className="text-xl font-bold mb-2">Users</h3>
            <p className="text-sm text-muted-foreground">Manage customers, merchants, and admins.</p>
          </Link>
          <Link href="/admin/audit-logs" className="glass rounded-2xl p-8 border border-border hover:border-primary/50 transition-colors group text-center">
            <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4 group-hover:text-primary transition-colors" />
            <h3 className="text-xl font-bold mb-2">Audit Logs</h3>
            <p className="text-sm text-muted-foreground">View system-wide security audit trail.</p>
          </Link>
          <Link href="/admin/agent-activity" className="glass rounded-2xl p-8 border border-border hover:border-primary/50 transition-colors group text-center">
            <Activity className="w-12 h-12 text-muted-foreground mx-auto mb-4 group-hover:text-primary transition-colors" />
            <h3 className="text-xl font-bold mb-2">Agent Activity</h3>
            <p className="text-sm text-muted-foreground">Monitor AI tool usage and telemetry.</p>
          </Link>
        </div>
      </main>
    </div>
  );
}

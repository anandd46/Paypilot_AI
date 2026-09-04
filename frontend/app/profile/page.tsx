"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { User, Mail, Shield, LogOut, ArrowRight, Package, Loader2, Zap } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import api, { type User as UserType } from "@/lib/api";

export default function ProfilePage() {
  const { isAuthenticated, logout, isMerchant, isAdmin } = useAuth();
  const router = useRouter();
  const [user, setUser] = useState<UserType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login?redirect=/profile");
      return;
    }
    fetchProfile();
  }, [isAuthenticated, router]);

  const fetchProfile = async () => {
    try {
      const data = await api.getMe();
      setUser(data);
    } catch (err) {
      console.error("Failed to fetch profile", err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push("/");
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-background text-foreground pb-20">
      <header className="glass sticky top-0 z-50 border-b border-border px-6 py-4 mb-8">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center">
              <Zap className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-bold gradient-text">PayPilot AI</span>
          </Link>
          <Link href="/dashboard" className="text-sm font-medium hover:text-primary transition-colors">
            Dashboard
          </Link>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6">
        <h1 className="text-3xl font-bold mb-8">My Profile</h1>

        <div className="space-y-6">
          <div className="glass rounded-3xl p-8 border border-border flex flex-col md:flex-row items-center gap-6 text-center md:text-left animate-fade-in">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center text-3xl font-bold text-white shadow-lg shrink-0">
              {user.name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h2 className="text-2xl font-bold mb-1">{user.name}</h2>
              <div className="flex items-center justify-center md:justify-start gap-2 text-muted-foreground mb-3">
                <Mail className="w-4 h-4" />
                {user.email}
              </div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border bg-secondary/50 text-xs font-medium capitalize">
                <Shield className="w-3.5 h-3.5" />
                {user.role} Account
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Link href="/orders" className="glass rounded-2xl p-6 border border-border hover:border-primary/50 hover:bg-primary/5 transition-all group animate-fade-in">
              <div className="w-12 h-12 rounded-xl bg-secondary flex items-center justify-center mb-4 group-hover:bg-primary/10 transition-colors">
                <Package className="w-6 h-6 text-muted-foreground group-hover:text-primary transition-colors" />
              </div>
              <h3 className="text-lg font-bold mb-1 group-hover:text-primary transition-colors">My Orders</h3>
              <p className="text-sm text-muted-foreground mb-4">View your purchase history and track shipments.</p>
              <div className="flex items-center text-sm font-medium text-primary gap-1">
                View history <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>

            {(isMerchant || isAdmin) && (
              <Link href="/merchant" className="glass rounded-2xl p-6 border border-border hover:border-primary/50 hover:bg-primary/5 transition-all group animate-fade-in" style={{ animationDelay: "100ms" }}>
                <div className="w-12 h-12 rounded-xl bg-secondary flex items-center justify-center mb-4 group-hover:bg-primary/10 transition-colors">
                  <Shield className="w-6 h-6 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
                <h3 className="text-lg font-bold mb-1 group-hover:text-primary transition-colors">Merchant Dashboard</h3>
                <p className="text-sm text-muted-foreground mb-4">Manage products, orders, and view AI analytics.</p>
                <div className="flex items-center text-sm font-medium text-primary gap-1">
                  Go to dashboard <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            )}
          </div>

          <div className="pt-8">
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 text-rose-400 hover:text-rose-500 font-medium transition-colors px-4 py-2 hover:bg-rose-400/10 rounded-lg"
            >
              <LogOut className="w-5 h-5" />
              Sign Out
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

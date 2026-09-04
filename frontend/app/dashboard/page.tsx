"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import api, { type Order, type PaginatedResponse } from "@/lib/api";
import {
  Zap, ShoppingBag, Bot, LogOut, Loader2, Package,
  Clock, CheckCircle, XCircle, CreditCard, ChevronRight,
} from "lucide-react";

const STATUS_CONFIG: Record<string, { label: string; color: string; icon: React.ComponentType<{ className?: string }> }> = {
  paid: { label: "Paid", color: "text-emerald-400 bg-emerald-400/10", icon: CheckCircle },
  completed: { label: "Completed", color: "text-emerald-400 bg-emerald-400/10", icon: CheckCircle },
  pending_payment: { label: "Pending Payment", color: "text-amber-400 bg-amber-400/10", icon: Clock },
  payment_failed: { label: "Payment Failed", color: "text-rose-400 bg-rose-400/10", icon: XCircle },
  draft: { label: "Draft", color: "text-muted-foreground bg-secondary", icon: Package },
  cancelled: { label: "Cancelled", color: "text-rose-400 bg-rose-400/10", icon: XCircle },
  shipped: { label: "Shipped", color: "text-blue-400 bg-blue-400/10", icon: Package },
  delivered: { label: "Delivered", color: "text-emerald-400 bg-emerald-400/10", icon: CheckCircle },
};

export default function CustomerDashboard() {
  const { user, logout, isAuthenticated } = useAuth();
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) { router.push("/login"); return; }
    api.getOrders(1, 10).then(d => { setOrders(d.items); setLoading(false); }).catch(() => setLoading(false));
  }, [isAuthenticated]);

  const handleLogout = () => { logout(); router.push("/"); };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;
  }

  return (
    <div className="min-h-screen">
      <header className="glass sticky top-0 z-50 border-b border-border px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center">
              <Zap className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-bold gradient-text">PayPilot AI</span>
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/shop" className="text-sm text-muted-foreground hover:text-foreground">Shop</Link>
            <Link href="/chat" className="text-sm text-muted-foreground hover:text-foreground">AI Chat</Link>
            <button onClick={handleLogout} className="glass px-3 py-2 rounded-lg text-sm hover:bg-card flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Welcome */}
        <div className="glass rounded-2xl p-6 border border-border mb-8 flex items-center justify-between">
          <div>
            <div className="text-xs text-muted-foreground mb-1">Welcome back</div>
            <h1 className="text-2xl font-bold">{user?.name}</h1>
            <div className="text-sm text-muted-foreground">{user?.email}</div>
          </div>
          <div className="flex gap-3">
            <Link href="/chat" className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-violet-500 text-white px-4 py-2 rounded-xl text-sm font-medium hover:opacity-90">
              <Bot className="w-4 h-4" /> AI Assistant
            </Link>
            <Link href="/shop" className="flex items-center gap-2 glass px-4 py-2 rounded-xl text-sm hover:bg-card transition-colors">
              <ShoppingBag className="w-4 h-4" /> Shop
            </Link>
          </div>
        </div>

        {/* Orders */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">My Orders</h2>
            <span className="text-sm text-muted-foreground">{orders.length} orders</span>
          </div>

          {orders.length === 0 ? (
            <div className="glass rounded-2xl p-12 text-center border border-border">
              <ShoppingBag className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="font-semibold mb-2">No orders yet</h3>
              <p className="text-muted-foreground text-sm mb-6">Start shopping with AI guidance</p>
              <div className="flex gap-3 justify-center">
                <Link href="/chat" className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-violet-500 text-white px-5 py-2.5 rounded-xl text-sm">
                  <Bot className="w-4 h-4" /> Get AI Recommendations
                </Link>
                <Link href="/shop" className="glass px-5 py-2.5 rounded-xl text-sm hover:bg-card transition-colors">Browse Shop</Link>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {orders.map((order) => {
                const statusCfg = STATUS_CONFIG[order.status] || STATUS_CONFIG.draft;
                const StatusIcon = statusCfg.icon;
                return (
                  <div key={order.id} className="glass rounded-2xl p-5 border border-border hover:border-border/80 transition-all">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                          <div className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full ${statusCfg.color}`}>
                            <StatusIcon className="w-3 h-3" />
                            {statusCfg.label}
                          </div>
                          <span className="text-xs text-muted-foreground">
                            {new Date(order.created_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground font-mono truncate mb-2">
                          {order.id}
                        </div>
                        {order.items?.slice(0, 2).map((item) => (
                          <div key={item.id} className="text-sm text-muted-foreground truncate">
                            {item.quantity}× {item.product_name}
                          </div>
                        ))}
                        {order.items?.length > 2 && (
                          <div className="text-xs text-muted-foreground mt-1">+{order.items.length - 2} more items</div>
                        )}
                      </div>
                      <div className="text-right flex-shrink-0">
                        <div className="text-xl font-bold text-primary">₹{order.amount.toLocaleString()}</div>
                        <div className="text-xs text-muted-foreground">{order.currency}</div>
                        {order.payments?.[0] && (
                          <div className="flex items-center gap-1 justify-end mt-2 text-xs text-muted-foreground">
                            <CreditCard className="w-3 h-3" />
                            {order.payments[0].provider}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Package, Clock, CheckCircle2, XCircle, ArrowRight, Zap } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import api, { type Order } from "@/lib/api";

export default function OrdersPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login?redirect=/orders");
      return;
    }
    fetchOrders();
  }, [isAuthenticated, router]);

  const fetchOrders = async () => {
    try {
      const data = await api.getOrders(1, 20);
      setOrders(data.items);
    } catch (err) {
      console.error("Failed to fetch orders", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 rounded-full border-4 border-primary border-t-transparent animate-spin" />
      </div>
    );
  }

  const getStatusConfig = (status: string) => {
    switch (status) {
      case "completed": return { icon: CheckCircle2, color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20" };
      case "cancelled": case "payment_failed": return { icon: XCircle, color: "text-rose-400 bg-rose-400/10 border-rose-400/20" };
      default: return { icon: Clock, color: "text-amber-400 bg-amber-400/10 border-amber-400/20" };
    }
  };

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
            Back to Dashboard
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6">
        <h1 className="text-3xl font-bold mb-8">My Orders</h1>

        {orders.length === 0 ? (
          <div className="glass rounded-2xl p-16 text-center border border-border">
            <Package className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-bold mb-2">No orders yet</h2>
            <p className="text-muted-foreground mb-6">When you buy something, it will appear here.</p>
            <Link href="/shop" className="inline-flex items-center gap-2 bg-primary text-primary-foreground px-6 py-3 rounded-xl font-medium hover:bg-primary/90 transition-colors">
              Start Shopping
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map(order => {
              const { icon: StatusIcon, color } = getStatusConfig(order.status);
              return (
                <div key={order.id} className="glass rounded-2xl border border-border overflow-hidden hover:border-border/80 transition-colors animate-fade-in">
                  <div className="p-5 flex flex-col md:flex-row gap-4 items-start md:items-center justify-between border-b border-border/50 bg-card/30">
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Order {order.id.split("-")[0]}</div>
                      <div className="text-sm font-medium">{new Date(order.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</div>
                    </div>
                    <div className="flex items-center gap-4 w-full md:w-auto justify-between md:justify-end">
                      <div className="text-right">
                        <div className="text-xs text-muted-foreground mb-1">Total</div>
                        <div className="font-bold text-primary">₹{order.amount.toLocaleString()}</div>
                      </div>
                      <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-medium ${color}`}>
                        <StatusIcon className="w-3.5 h-3.5" />
                        <span className="capitalize">{order.status.replace("_", " ")}</span>
                      </div>
                    </div>
                  </div>
                  <div className="p-5">
                    <div className="flex flex-wrap gap-4 items-center">
                      {order.items.slice(0, 4).map(item => (
                        <div key={item.id} className="flex items-center gap-3 bg-background/50 border border-border rounded-lg p-2 pr-4 w-full md:w-auto min-w-[200px]">
                          <div className="w-10 h-10 rounded-md bg-secondary flex items-center justify-center shrink-0">
                            <Package className="w-5 h-5 text-muted-foreground" />
                          </div>
                          <div className="truncate">
                            <div className="text-sm font-medium truncate max-w-[150px]">{item.product_name}</div>
                            <div className="text-xs text-muted-foreground">Qty: {item.quantity}</div>
                          </div>
                        </div>
                      ))}
                      {order.items.length > 4 && (
                        <div className="text-sm text-muted-foreground font-medium px-2">
                          +{order.items.length - 4} more items
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="p-4 border-t border-border/50 bg-card/30 flex justify-end">
                    <Link href={`/orders/${order.id}`} className="flex items-center gap-1.5 text-sm font-medium text-primary hover:text-primary/80 transition-colors">
                      View details <ArrowRight className="w-4 h-4" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}

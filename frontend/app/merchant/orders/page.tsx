"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Zap, Package, Search, Loader2, ArrowLeft, Clock, CheckCircle2, XCircle } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import api, { type Order } from "@/lib/api";

export default function MerchantOrdersPage() {
  const { isAuthenticated, isMerchant, isAdmin } = useAuth();
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    if (!isAuthenticated) { router.push("/login?redirect=/merchant/orders"); return; }
    if (!isMerchant && !isAdmin) { router.push("/"); return; }
    loadOrders();
  }, [isAuthenticated, isMerchant, isAdmin]);

  const loadOrders = async () => {
    try {
      const data = await api.getOrders(1, 100);
      setOrders(data.items);
    } catch (err) {
      console.error("Failed to load orders");
    } finally {
      setLoading(false);
    }
  };

  const filteredOrders = orders.filter(o => 
    o.id.toLowerCase().includes(search.toLowerCase()) || 
    o.status.toLowerCase().includes(search.toLowerCase())
  );

  const getStatusConfig = (status: string) => {
    switch (status) {
      case "completed": return { icon: CheckCircle2, color: "text-emerald-400 bg-emerald-400/10 border-emerald-400/20" };
      case "cancelled": case "payment_failed": return { icon: XCircle, color: "text-rose-400 bg-rose-400/10 border-rose-400/20" };
      default: return { icon: Clock, color: "text-amber-400 bg-amber-400/10 border-amber-400/20" };
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="glass sticky top-0 z-50 border-b border-border px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center">
                <Zap className="w-3.5 h-3.5 text-white" />
              </div>
              <span className="font-bold gradient-text">PayPilot AI</span>
            </Link>
            <nav className="hidden md:flex items-center gap-4 text-sm">
              <Link href="/merchant" className="text-muted-foreground hover:text-foreground transition-colors">Overview</Link>
              <Link href="/merchant/products" className="text-muted-foreground hover:text-foreground transition-colors">Products</Link>
              <Link href="/merchant/orders" className="text-primary font-medium">Orders</Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">Order Management</h1>
            <p className="text-muted-foreground">View and track all customer orders</p>
          </div>
        </div>

        <div className="glass rounded-2xl border border-border overflow-hidden animate-fade-in">
          <div className="p-4 border-b border-border bg-card/50 flex flex-col md:flex-row gap-4 justify-between items-center">
            <div className="relative w-full md:w-96">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search by order ID or status..."
                value={search}
                onChange={e => setSearch(e.target.value)}
                className="w-full bg-background border border-border rounded-xl pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-primary/50"
              />
            </div>
            <div className="text-sm text-muted-foreground whitespace-nowrap">
              {filteredOrders.length} orders
            </div>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-border text-xs uppercase tracking-wider text-muted-foreground bg-secondary/30">
                  <th className="px-6 py-4 font-medium">Order ID</th>
                  <th className="px-6 py-4 font-medium">Date</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4 font-medium">Amount</th>
                  <th className="px-6 py-4 font-medium">Items</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredOrders.map(order => {
                  const { icon: StatusIcon, color } = getStatusConfig(order.status);
                  return (
                    <tr key={order.id} className="hover:bg-secondary/30 transition-colors">
                      <td className="px-6 py-4 font-mono text-xs">
                        {order.id.split('-')[0]}
                      </td>
                      <td className="px-6 py-4 text-sm whitespace-nowrap">
                        {new Date(order.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${color}`}>
                          <StatusIcon className="w-3.5 h-3.5" />
                          <span className="capitalize">{order.status.replace("_", " ")}</span>
                        </span>
                      </td>
                      <td className="px-6 py-4 font-medium text-primary">
                        ₹{order.amount.toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        {order.items?.length || 0} items
                      </td>
                    </tr>
                  )
                })}
                {filteredOrders.length === 0 && (
                  <tr>
                    <td colSpan={5} className="px-6 py-12 text-center text-muted-foreground">
                      No orders found matching "{search}"
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}

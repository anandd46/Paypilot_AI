"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Package, Clock, CheckCircle2, XCircle, CreditCard, AlertTriangle, Loader2 } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import api, { type Order } from "@/lib/api";

export default function OrderDetailPage() {
  const { id } = useParams();
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push(`/login?redirect=/orders/${id}`);
      return;
    }
    fetchOrder();
  }, [id, isAuthenticated, router]);

  const fetchOrder = async () => {
    try {
      if (typeof id === "string") {
        const data = await api.getOrder(id);
        setOrder(data);
      }
    } catch (err) {
      console.error("Failed to fetch order", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;
  }

  if (!order) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-center px-4">
        <AlertTriangle className="w-16 h-16 text-amber-400 mb-4" />
        <h1 className="text-2xl font-bold mb-2">Order Not Found</h1>
        <p className="text-muted-foreground mb-6">This order might have been deleted or doesn't belong to you.</p>
        <Link href="/orders" className="bg-primary text-primary-foreground px-6 py-3 rounded-xl font-medium">Back to Orders</Link>
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
  const { icon: StatusIcon, color: statusColor } = getStatusConfig(order.status);

  return (
    <div className="min-h-screen bg-background text-foreground pb-20">
      <header className="glass sticky top-0 z-50 border-b border-border px-6 py-4 mb-8">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Link href="/orders" className="flex items-center gap-2 text-sm font-medium hover:text-primary transition-colors">
            <ArrowLeft className="w-4 h-4" /> Back to Orders
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">Order Details</h1>
            <p className="text-muted-foreground font-mono text-sm">ID: {order.id}</p>
            <p className="text-muted-foreground text-sm mt-1">Placed on {new Date(order.created_at).toLocaleString()}</p>
          </div>
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full border font-medium ${statusColor} shrink-0`}>
            <StatusIcon className="w-4 h-4" />
            <span className="capitalize">{order.status.replace("_", " ")}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-6">
            <div className="glass rounded-2xl border border-border p-6 animate-fade-in">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Package className="w-5 h-5 text-primary" /> Items
              </h2>
              <div className="space-y-4">
                {order.items.map(item => (
                  <div key={item.id} className="flex justify-between items-center py-3 border-b border-border/50 last:border-0">
                    <div>
                      <div className="font-medium">{item.product_name}</div>
                      <div className="text-sm text-muted-foreground">Qty: {item.quantity}</div>
                    </div>
                    <div className="font-medium text-primary">₹{(item.price * item.quantity).toLocaleString()}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="glass rounded-2xl border border-border p-6 sticky top-24 animate-fade-in">
              <h2 className="text-xl font-bold mb-4">Summary</h2>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Subtotal</span>
                  <span>₹{order.amount.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Shipping</span>
                  <span className="text-emerald-400">Free</span>
                </div>
                <div className="border-t border-border pt-3 mt-3 flex justify-between font-bold text-lg">
                  <span>Total</span>
                  <span className="text-primary">₹{order.amount.toLocaleString()}</span>
                </div>
              </div>

              {order.payments && order.payments.length > 0 && (
                <div className="mt-6 pt-6 border-t border-border">
                  <h3 className="font-semibold mb-3 flex items-center gap-2 text-sm">
                    <CreditCard className="w-4 h-4" /> Payment Info
                  </h3>
                  {order.payments.map(payment => (
                    <div key={payment.id} className="text-xs space-y-1 bg-secondary/50 rounded-lg p-3">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Provider:</span>
                        <span className="capitalize">{payment.provider}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Status:</span>
                        <span className="capitalize font-medium text-emerald-400">{payment.status}</span>
                      </div>
                      {payment.razorpay_payment_id && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Txn ID:</span>
                          <span className="font-mono text-muted-foreground max-w-[100px] truncate">{payment.razorpay_payment_id}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

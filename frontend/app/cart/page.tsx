"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ShoppingCart, Plus, Minus, Trash2, Zap, ArrowLeft, CreditCard,
  Package, Loader2, CheckCircle, XCircle, AlertTriangle, Bot,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import api, { type Cart, type CheckoutResponse } from "@/lib/api";

type CheckoutState = "idle" | "processing" | "success" | "failed";

export default function CartPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState<string | null>(null);
  const [checkoutState, setCheckoutState] = useState<CheckoutState>("idle");
  const [checkoutData, setCheckoutData] = useState<CheckoutResponse | null>(null);
  const [paymentResult, setPaymentResult] = useState<"success" | "failed" | null>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login?redirect=/cart");
      return;
    }
    fetchCart();
  }, [isAuthenticated]);

  const fetchCart = async () => {
    try {
      const data = await api.getCart();
      setCart(data);
    } catch (err) {
      console.error("Failed to fetch cart:", err);
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (itemId: string, quantity: number) => {
    if (quantity < 1) return;
    setUpdating(itemId);
    try {
      const updated = await api.updateCartItem(itemId, quantity);
      setCart(updated);
    } catch (err) {
      console.error("Failed to update:", err);
    } finally {
      setUpdating(null);
    }
  };

  const removeItem = async (itemId: string) => {
    setUpdating(itemId);
    try {
      const updated = await api.removeCartItem(itemId);
      setCart(updated);
    } finally {
      setUpdating(null);
    }
  };

  const handleCheckout = async () => {
    setCheckoutState("processing");
    try {
      const data = await api.createCheckout();
      setCheckoutData(data);

      if (data.is_demo) {
        // Demo payment flow
        await new Promise(r => setTimeout(r, 1500)); // Simulate processing
        const result = await api.verifyDemoPayment(data.order_id, false);
        setPaymentResult("success");
        setCheckoutState("success");
        setCart(null);
      } else {
        // Razorpay real payment flow
        const options = {
          key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
          amount: data.amount * 100,
          currency: "INR",
          order_id: data.razorpay_order_id,
          name: "PayPilot AI",
          description: "Order Payment",
          handler: async (response: { razorpay_payment_id: string; razorpay_order_id: string; razorpay_signature: string }) => {
            try {
              await api.verifyPayment({
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
                order_id: data.order_id,
              });
              setPaymentResult("success");
              setCheckoutState("success");
              setCart(null);
            } catch {
              setPaymentResult("failed");
              setCheckoutState("failed");
            }
          },
          modal: {
            ondismiss: () => setCheckoutState("idle"),
          },
        };
        // @ts-ignore
        const rzp = new window.Razorpay(options);
        rzp.open();
      }
    } catch (err) {
      setCheckoutState("failed");
    }
  };

  const simulateFailure = async () => {
    if (!checkoutData) return;
    setCheckoutState("processing");
    await new Promise(r => setTimeout(r, 1000));
    await api.verifyDemoPayment(checkoutData.order_id, true);
    setPaymentResult("failed");
    setCheckoutState("failed");
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  // Success state
  if (checkoutState === "success") {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="glass rounded-3xl p-12 text-center max-w-md w-full animate-fade-in">
          <div className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-emerald-400" />
          </div>
          <h2 className="text-2xl font-bold mb-2">Payment Successful!</h2>
          <p className="text-muted-foreground mb-2">Your order has been confirmed and inventory reserved.</p>
          {checkoutData?.is_demo && (
            <div className="inline-flex items-center gap-2 text-amber-400 text-xs bg-amber-400/10 border border-amber-400/20 px-3 py-1.5 rounded-full mb-6">
              <AlertTriangle className="w-3 h-3" />
              Demo Payment Mode
            </div>
          )}
          <div className="glass rounded-xl p-4 mb-6 text-left">
            <div className="text-xs text-muted-foreground mb-1">Order Amount</div>
            <div className="text-2xl font-bold text-primary">₹{checkoutData?.amount.toLocaleString()}</div>
            {checkoutData?.order_id && (
              <div className="text-xs text-muted-foreground mt-2 font-mono truncate">
                Order: {checkoutData.order_id}
              </div>
            )}
          </div>
          <div className="flex flex-col gap-3">
            <Link href="/dashboard" className="flex items-center justify-center gap-2 bg-gradient-to-r from-cyan-500 to-violet-500 text-white px-6 py-3 rounded-xl font-medium">
              View My Orders
            </Link>
            <Link href="/shop" className="glass px-6 py-3 rounded-xl text-center font-medium hover:bg-card transition-colors">
              Continue Shopping
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const isEmpty = !cart || cart.items.length === 0;

  return (
    <div className="min-h-screen">
      <header className="glass sticky top-0 z-50 border-b border-border px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/" className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center">
                <Zap className="w-3.5 h-3.5 text-white" />
              </div>
              <span className="font-bold gradient-text">PayPilot AI</span>
            </Link>
          </div>
          <Link href="/shop" className="flex items-center gap-2 glass px-3 py-2 rounded-lg text-sm hover:bg-card transition-colors">
            <ArrowLeft className="w-4 h-4" /> Continue Shopping
          </Link>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-bold mb-8 flex items-center gap-3">
          <ShoppingCart className="w-6 h-6 text-primary" />
          Your Cart
          {cart && cart.item_count > 0 && (
            <span className="text-sm font-normal text-muted-foreground">({cart.item_count} items)</span>
          )}
        </h1>

        {isEmpty ? (
          <div className="glass rounded-2xl p-16 text-center">
            <ShoppingCart className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">Your cart is empty</h3>
            <p className="text-muted-foreground mb-8">Let the AI assistant help you find the perfect products</p>
            <div className="flex gap-3 justify-center">
              <Link href="/chat" className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-violet-500 text-white px-6 py-3 rounded-xl">
                <Bot className="w-4 h-4" /> AI Assistant
              </Link>
              <Link href="/shop" className="glass px-6 py-3 rounded-xl hover:bg-card transition-colors">
                Browse Shop
              </Link>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Items */}
            <div className="lg:col-span-2 space-y-4">
              {cart.items.map((item) => (
                <div key={item.id} className="glass rounded-2xl p-4 border border-border flex gap-4 animate-fade-in">
                  <div className="w-20 h-20 rounded-xl bg-secondary flex items-center justify-center flex-shrink-0 overflow-hidden">
                    {item.product?.image_url ? (
                      <img src={item.product.image_url} alt={item.product.name} className="w-full h-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
                    ) : (
                      <Package className="w-8 h-8 text-muted-foreground" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-sm leading-snug mb-1 truncate">{item.product?.name}</h4>
                    <p className="text-xs text-muted-foreground mb-3">{item.product?.brand} · {item.product?.category}</p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 glass rounded-lg px-2 py-1">
                        <button onClick={() => updateQuantity(item.id, item.quantity - 1)} disabled={updating === item.id || item.quantity <= 1} className="text-muted-foreground hover:text-foreground disabled:opacity-40 transition-colors">
                          <Minus className="w-3 h-3" />
                        </button>
                        <span className="text-sm w-6 text-center font-medium">
                          {updating === item.id ? <Loader2 className="w-3 h-3 animate-spin mx-auto" /> : item.quantity}
                        </span>
                        <button onClick={() => updateQuantity(item.id, item.quantity + 1)} disabled={updating === item.id} className="text-muted-foreground hover:text-foreground disabled:opacity-40 transition-colors">
                          <Plus className="w-3 h-3" />
                        </button>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-primary">₹{item.total_price.toLocaleString()}</div>
                        <div className="text-xs text-muted-foreground">₹{item.unit_price.toLocaleString()} each</div>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => removeItem(item.id)}
                    disabled={updating === item.id}
                    className="text-muted-foreground hover:text-destructive transition-colors self-start"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>

            {/* Summary */}
            <div>
              <div className="glass rounded-2xl p-6 border border-border sticky top-24">
                <h3 className="font-semibold mb-4">Order Summary</h3>
                <div className="space-y-2 text-sm mb-4">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Subtotal</span>
                    <span>₹{cart.subtotal.toLocaleString()}</span>
                  </div>
                  {cart.discount > 0 && (
                    <div className="flex justify-between text-emerald-400">
                      <span>Discount</span>
                      <span>-₹{cart.discount.toLocaleString()}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Shipping</span>
                    <span className="text-emerald-400">Free</span>
                  </div>
                  <div className="border-t border-border pt-2 flex justify-between font-bold text-lg">
                    <span>Total</span>
                    <span className="text-primary">₹{cart.total.toLocaleString()}</span>
                  </div>
                </div>

                <div className="space-y-3">
                  <button
                    onClick={handleCheckout}
                    disabled={checkoutState === "processing"}
                    id="checkout-button"
                    className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-cyan-500 to-violet-500 text-white px-6 py-3 rounded-xl font-medium hover:opacity-90 transition-all disabled:opacity-70"
                  >
                    {checkoutState === "processing" ? (
                      <><Loader2 className="w-4 h-4 animate-spin" /> Processing...</>
                    ) : (
                      <><CreditCard className="w-4 h-4" /> Proceed to Payment</>
                    )}
                  </button>

                  <div className="text-xs text-muted-foreground text-center space-y-1">
                    <div className="flex items-center gap-1 justify-center">
                      <AlertTriangle className="w-3 h-3 text-amber-400" />
                      Demo Mode — No real payment charged
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

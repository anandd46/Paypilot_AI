"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  BarChart3, TrendingUp, ShoppingBag, Users, CreditCard,
  Bot, Activity, Package, Zap, ArrowUp, ArrowDown, Loader2,
  RefreshCw, AlertTriangle, Target, DollarSign, Star,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import api, { type AnalyticsOverview } from "@/lib/api";
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, BarChart, Bar, Cell, PieChart, Pie, Legend,
} from "recharts";

interface RevenuePoint { date: string; revenue: number; orders: number; ai_revenue: number; }

function MetricCard({ title, value, subtitle, icon: Icon, trend, color, suffix = "" }: {
  title: string; value: string | number; subtitle?: string;
  icon: React.ComponentType<{ className?: string }>; trend?: number; color: string; suffix?: string;
}) {
  return (
    <div className="glass rounded-2xl p-5 border border-border hover:border-border/80 transition-all">
      <div className="flex items-start justify-between mb-4">
        <div className={`w-10 h-10 rounded-xl ${color} flex items-center justify-center`}>
          <Icon className="w-5 h-5" />
        </div>
        {trend !== undefined && (
          <div className={`flex items-center gap-1 text-xs px-2 py-1 rounded-full ${
            trend >= 0 ? "text-emerald-400 bg-emerald-400/10" : "text-rose-400 bg-rose-400/10"
          }`}>
            {trend >= 0 ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
            {Math.abs(trend)}%
          </div>
        )}
      </div>
      <div className="text-2xl font-bold mb-1">{value}{suffix}</div>
      <div className="text-sm text-muted-foreground">{title}</div>
      {subtitle && <div className="text-xs text-muted-foreground/70 mt-1">{subtitle}</div>}
    </div>
  );
}

const COLORS = ["#06b6d4", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"];

export default function MerchantDashboard() {
  const { isAuthenticated, isMerchant, isAdmin, user } = useAuth();
  const router = useRouter();
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [revenue, setRevenue] = useState<RevenuePoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) { router.push("/login?redirect=/merchant"); return; }
    if (!isMerchant && !isAdmin) { router.push("/dashboard"); return; }
    fetchData();
  }, [isAuthenticated, isMerchant, isAdmin]);

  const fetchData = async () => {
    try {
      const [ov, rev] = await Promise.all([
        api.getAnalyticsOverview(),
        api.getRevenueData(30),
      ]);
      setOverview(ov);
      setRevenue(rev);
    } catch (err) {
      console.error("Failed to fetch analytics:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const refresh = async () => { setRefreshing(true); await fetchData(); };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  const aiShare = overview ? Math.round(overview.ai_assisted_revenue / Math.max(overview.total_revenue, 1) * 100) : 0;

  const pieData = overview ? [
    { name: "AI-Assisted", value: Math.round(overview.ai_assisted_revenue) },
    { name: "Organic", value: Math.round(overview.total_revenue - overview.ai_assisted_revenue) },
  ] : [];

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="glass sticky top-0 z-50 border-b border-border px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-cyan-500 to-violet-500 flex items-center justify-center">
              <Zap className="w-3.5 h-3.5 text-white" />
            </div>
            <span className="font-bold gradient-text">PayPilot AI</span>
          </Link>
          <div className="flex items-center gap-3">
            {overview?.is_demo && (
              <span className="text-xs status-demo px-3 py-1 rounded-full flex items-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                Demo Data
              </span>
            )}
            <button onClick={refresh} disabled={refreshing} className="glass px-3 py-2 rounded-lg text-sm hover:bg-card transition-colors flex items-center gap-2">
              <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
              Refresh
            </button>
            <Link href="/shop" className="text-sm text-muted-foreground hover:text-foreground">Shop</Link>
            <span className="text-sm text-muted-foreground">{user?.name}</span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Merchant Dashboard</h1>
            <p className="text-muted-foreground mt-1">PayPilot AI Analytics — Last 30 days</p>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/chat" className="flex items-center gap-2 glass px-4 py-2 rounded-xl text-sm hover:bg-card transition-colors">
              <Bot className="w-4 h-4 text-cyan-400" />
              AI Assistant
            </Link>
          </div>
        </div>

        {/* KPI Cards */}
        {overview && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-8">
            <MetricCard
              title="Total Revenue"
              value={`₹${(overview.total_revenue / 1000).toFixed(0)}K`}
              subtitle="Last 30 days"
              icon={DollarSign}
              trend={12}
              color="bg-cyan-500/20 text-cyan-400"
            />
            <MetricCard
              title="Total Orders"
              value={overview.total_orders.toLocaleString()}
              subtitle="Completed orders"
              icon={ShoppingBag}
              trend={8}
              color="bg-violet-500/20 text-violet-400"
            />
            <MetricCard
              title="Customers"
              value={overview.total_customers.toLocaleString()}
              subtitle="Unique buyers"
              icon={Users}
              trend={5}
              color="bg-emerald-500/20 text-emerald-400"
            />
            <MetricCard
              title="Avg Order Value"
              value={`₹${overview.avg_order_value.toLocaleString()}`}
              subtitle="Per transaction"
              icon={TrendingUp}
              trend={3}
              color="bg-amber-500/20 text-amber-400"
            />
            <MetricCard
              title="AI-Assisted Orders"
              value={overview.ai_assisted_orders.toLocaleString()}
              subtitle={`${aiShare}% of revenue`}
              icon={Bot}
              color="bg-blue-500/20 text-blue-400"
            />
            <MetricCard
              title="Upsell Revenue"
              value={`₹${(overview.upsell_revenue / 1000).toFixed(0)}K`}
              subtitle="From upsell conversions"
              icon={ArrowUp}
              color="bg-pink-500/20 text-pink-400"
            />
            <MetricCard
              title="Payment Success"
              value={overview.payment_success_rate.toFixed(1)}
              suffix="%"
              subtitle={`${overview.failed_payments} failed`}
              icon={CreditCard}
              color="bg-green-500/20 text-green-400"
            />
            <MetricCard
              title="Cross-sell Revenue"
              value={`₹${(overview.cross_sell_revenue / 1000).toFixed(0)}K`}
              subtitle="From accessory sales"
              icon={Target}
              color="bg-orange-500/20 text-orange-400"
            />
          </div>
        )}

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Revenue Chart */}
          <div className="lg:col-span-2 glass rounded-2xl p-6 border border-border">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="font-semibold">Revenue Over Time</h2>
                <p className="text-xs text-muted-foreground mt-0.5">Total vs AI-assisted revenue</p>
              </div>
              <Activity className="w-4 h-4 text-muted-foreground" />
            </div>
            {revenue.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={revenue} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
                  <defs>
                    <linearGradient id="totalGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="aiGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(222 47% 15%)" />
                  <XAxis dataKey="date" tick={{ fontSize: 10, fill: "hsl(210 20% 55%)" }} />
                  <YAxis tick={{ fontSize: 10, fill: "hsl(210 20% 55%)" }} />
                  <Tooltip
                    contentStyle={{ background: "hsl(222 47% 8%)", border: "1px solid hsl(222 47% 15%)", borderRadius: "12px" }}
                    labelStyle={{ color: "hsl(210 40% 95%)" }}
                    formatter={(value: any) => [`₹${value.toLocaleString()}`, ""]}
                  />
                  <Area type="monotone" dataKey="revenue" stroke="#06b6d4" fill="url(#totalGrad)" name="Total" strokeWidth={2} />
                  <Area type="monotone" dataKey="ai_revenue" stroke="#8b5cf6" fill="url(#aiGrad)" name="AI-Assisted" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[220px] flex items-center justify-center text-muted-foreground text-sm">
                No revenue data yet. Seed the database and complete some orders.
              </div>
            )}
          </div>

          {/* AI Share Pie */}
          <div className="glass rounded-2xl p-6 border border-border">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="font-semibold">Revenue Attribution</h2>
                <p className="text-xs text-muted-foreground">AI vs Organic</p>
              </div>
              <Bot className="w-4 h-4 text-cyan-400" />
            </div>
            {pieData.some(d => d.value > 0) ? (
              <ResponsiveContainer width="100%" height={180}>
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={75} paddingAngle={3} dataKey="value">
                    {pieData.map((entry, index) => (
                      <Cell key={entry.name} fill={COLORS[index]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v: any) => [`₹${v.toLocaleString()}`, "Revenue"]} contentStyle={{ background: "hsl(222 47% 8%)", border: "1px solid hsl(222 47% 15%)", borderRadius: "8px" }} />
                  <Legend formatter={(v) => <span style={{ color: "hsl(210 40% 80%)", fontSize: "12px" }}>{v}</span>} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[180px] flex items-center justify-center">
                <div className="text-center">
                  <div className="text-4xl font-bold gradient-text mb-2">{aiShare}%</div>
                  <div className="text-sm text-muted-foreground">AI-Assisted Revenue Share</div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Orders Bar Chart */}
        {revenue.length > 0 && (
          <div className="glass rounded-2xl p-6 border border-border mb-8">
            <h2 className="font-semibold mb-6">Daily Orders</h2>
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={revenue.slice(-14)} margin={{ top: 5, right: 5, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(222 47% 15%)" />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: "hsl(210 20% 55%)" }} />
                <YAxis tick={{ fontSize: 10, fill: "hsl(210 20% 55%)" }} />
                <Tooltip contentStyle={{ background: "hsl(222 47% 8%)", border: "1px solid hsl(222 47% 15%)", borderRadius: "8px" }} />
                <Bar dataKey="orders" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="Orders" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Quick links */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "AI Activity Log", href: "/merchant/activity", icon: Activity, desc: "Agent actions & telemetry" },
            { label: "Product Manager", href: "/merchant/products", icon: Package, desc: "Add, edit, manage products" },
            { label: "All Orders", href: "/dashboard", icon: ShoppingBag, desc: "View all customer orders" },
            { label: "AI Chat", href: "/chat", icon: Bot, desc: "Test the AI assistant" },
          ].map((item) => (
            <Link key={item.label} href={item.href} className="glass rounded-xl p-4 border border-border hover:border-primary/30 transition-all hover:scale-[1.02]">
              <item.icon className="w-5 h-5 text-primary mb-3" />
              <div className="font-medium text-sm">{item.label}</div>
              <div className="text-xs text-muted-foreground mt-1">{item.desc}</div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}

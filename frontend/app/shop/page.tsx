"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Search, SlidersHorizontal, Star, ShoppingCart, Package,
  ChevronLeft, ChevronRight, Loader2, X, Filter, Zap, Bot,
  TrendingUp, Smartphone, Laptop, Headphones, Camera, Watch,
  Tablet, Speaker, Mouse, Gamepad2, Box,
} from "lucide-react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import api, { type Product, type PaginatedResponse } from "@/lib/api";
import { useRouter } from "next/navigation";

const CATEGORIES = [
  "All", "Smartphones", "Laptops", "Headphones", "Gaming",
  "Cameras", "Smartwatches", "Tablets", "Speakers", "Laptop Accessories",
];

function ProductCard({ product, onAddToCart }: { product: Product; onAddToCart: (id: string) => void }) {
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);
  const [imgError, setImgError] = useState(false);

  const CategoryIcon = () => {
    const cat = product.category?.toLowerCase() ?? "";
    const cls = "w-14 h-14 opacity-80";
    if (cat.includes("smartphone") || cat.includes("phone")) return <Smartphone className={cls} />;
    if (cat.includes("laptop") || cat.includes("notebook")) return <Laptop className={cls} />;
    if (cat.includes("headphone") || cat.includes("earbud")) return <Headphones className={cls} />;
    if (cat.includes("camera")) return <Camera className={cls} />;
    if (cat.includes("smartwatch") || cat.includes("watch")) return <Watch className={cls} />;
    if (cat.includes("tablet")) return <Tablet className={cls} />;
    if (cat.includes("speaker")) return <Speaker className={cls} />;
    if (cat.includes("gaming")) return <Gamepad2 className={cls} />;
    if (cat.includes("accessory") || cat.includes("accessories")) return <Mouse className={cls} />;
    return <Box className={cls} />;
  };

  const CategoryGradient = () => {
    const cat = product.category?.toLowerCase() ?? "";
    if (cat.includes("smartphone")) return "from-blue-600/30 to-cyan-500/20";
    if (cat.includes("laptop")) return "from-violet-600/30 to-purple-500/20";
    if (cat.includes("headphone") || cat.includes("earbud")) return "from-rose-600/30 to-pink-500/20";
    if (cat.includes("camera")) return "from-amber-600/30 to-yellow-500/20";
    if (cat.includes("watch")) return "from-emerald-600/30 to-teal-500/20";
    if (cat.includes("tablet")) return "from-sky-600/30 to-blue-500/20";
    if (cat.includes("speaker")) return "from-orange-600/30 to-amber-500/20";
    if (cat.includes("gaming")) return "from-green-600/30 to-lime-500/20";
    return "from-slate-600/30 to-zinc-500/20";
  };


  const handleAdd = async () => {
    setAdding(true);
    try {
      await onAddToCart(product.id);
      setAdded(true);
      setTimeout(() => setAdded(false), 2000);
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="glass rounded-2xl overflow-hidden hover:border-primary/40 border border-border transition-all hover:scale-[1.01] hover:-translate-y-1 group">
      {/* Image */}
      <div className="h-48 bg-secondary flex items-center justify-center relative overflow-hidden">
        {product.image_url && !imgError ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className={`absolute inset-0 bg-gradient-to-br ${CategoryGradient()} flex flex-col items-center justify-center gap-2 text-foreground/60`}>
            <CategoryIcon />
            <span className="text-xs font-medium tracking-wide uppercase opacity-70">{product.brand || product.category}</span>
          </div>
        )}
        {product.discount_percent && (
          <div className="absolute top-3 left-3 bg-emerald-500 text-white text-xs font-bold px-2 py-1 rounded-full">
            -{product.discount_percent}%
          </div>
        )}
        {product.stock < 5 && product.stock > 0 && (
          <div className="absolute top-3 right-3 bg-amber-500/20 text-amber-400 border border-amber-500/30 text-xs px-2 py-1 rounded-full">
            Only {product.stock} left
          </div>
        )}
        {product.stock === 0 && (
          <div className="absolute inset-0 bg-background/60 flex items-center justify-center">
            <span className="text-sm text-muted-foreground font-medium">Out of Stock</span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="p-4">
        <div className="text-xs text-muted-foreground mb-1">{product.brand} · {product.category}</div>
        <h3 className="font-semibold text-sm mb-2 line-clamp-2 leading-snug">{product.name}</h3>

        <div className="flex items-center gap-1 mb-3">
          <div className="flex">
            {Array.from({ length: 5 }).map((_, i) => (
              <Star key={i} className={`w-3 h-3 ${i < Math.floor(product.rating) ? "text-amber-400 fill-amber-400" : "text-muted/30"}`} />
            ))}
          </div>
          <span className="text-xs text-muted-foreground">({product.review_count?.toLocaleString()})</span>
        </div>

        <div className="flex items-end justify-between">
          <div>
            <div className="text-xl font-bold text-primary">₹{product.price.toLocaleString()}</div>
            {product.original_price && product.original_price > product.price && (
              <div className="text-xs text-muted-foreground line-through">₹{product.original_price.toLocaleString()}</div>
            )}
          </div>
          <button
            onClick={handleAdd}
            disabled={adding || product.stock === 0}
            className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
              added
                ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                : "bg-primary/10 hover:bg-primary/20 text-primary border border-primary/30"
            }`}
          >
            {adding ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShoppingCart className="w-4 h-4" />}
            {added ? "Added!" : "Add"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function ShopPage() {
  const { isAuthenticated } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [sortBy, setSortBy] = useState("rating");
  const [maxPrice, setMaxPrice] = useState("");
  const [cartCount, setCartCount] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
  const LIMIT = 12;

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, unknown> = { page, limit: LIMIT, sort_by: sortBy };
      if (search) params.q = search;
      if (selectedCategory && selectedCategory !== "All") params.category = selectedCategory;
      if (maxPrice) params.max_price = parseFloat(maxPrice);

      const data = await api.getProducts(params as Parameters<typeof api.getProducts>[0]);
      setProducts(data.items);
      setTotal(data.total);
      setTotalPages(data.pages);
    } catch (err) {
      console.error("Failed to fetch products:", err);
    } finally {
      setLoading(false);
    }
  }, [page, search, selectedCategory, sortBy, maxPrice]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  useEffect(() => {
    if (isAuthenticated) {
      api.getCart().then(c => setCartCount(c.item_count)).catch(() => {});
    }
  }, [isAuthenticated]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchProducts();
  };

  const handleAddToCart = async (productId: string) => {
    if (!isAuthenticated) {
      window.location.href = "/login?redirect=/shop";
      return;
    }
    try {
      const cart = await api.addToCart(productId, 1);
      setCartCount(cart.item_count);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status?: number }; message?: string };
      if (axiosErr?.response?.status === 401) {
        window.location.href = "/login?redirect=/shop";
      } else {
        console.error("Add to cart failed:", axiosErr?.message ?? err);
      }
    }
  };

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
            <Link href="/chat" className="flex items-center gap-2 text-sm glass px-3 py-2 rounded-lg hover:bg-card transition-colors">
              <Bot className="w-4 h-4 text-cyan-400" />
              <span className="hidden md:block">AI Assistant</span>
            </Link>
            {isAuthenticated ? (
              <Link href="/cart" className="relative flex items-center gap-2 glass px-3 py-2 rounded-lg text-sm">
                <ShoppingCart className="w-4 h-4" />
                {cartCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 bg-primary text-primary-foreground text-xs rounded-full flex items-center justify-center">
                    {cartCount}
                  </span>
                )}
              </Link>
            ) : (
              <Link href="/login" className="text-sm bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90">
                Login
              </Link>
            )}
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Search & Filters */}
        <div className="flex flex-col gap-4 mb-8">
          <form onSubmit={handleSearch} className="flex gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search products, brands, categories..."
                className="w-full glass rounded-xl pl-10 pr-4 py-3 text-sm border border-border focus:border-primary/50 outline-none transition-colors"
                id="search-input"
              />
            </div>
            <select
              value={sortBy}
              onChange={(e) => { setSortBy(e.target.value); setPage(1); }}
              className="glass rounded-xl px-4 py-3 text-sm border border-border outline-none"
            >
              <option value="rating">Top Rated</option>
              <option value="price_asc">Price: Low to High</option>
              <option value="price_desc">Price: High to Low</option>
              <option value="newest">Newest</option>
            </select>
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className="glass rounded-xl px-4 py-3 border border-border hover:bg-card transition-colors"
            >
              <SlidersHorizontal className="w-4 h-4" />
            </button>
          </form>

          {showFilters && (
            <div className="glass rounded-xl p-4 border border-border animate-fade-in">
              <div className="flex items-center gap-4 flex-wrap">
                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">Max Price (₹)</label>
                  <input
                    type="number"
                    value={maxPrice}
                    onChange={(e) => { setMaxPrice(e.target.value); setPage(1); }}
                    placeholder="Any price"
                    className="glass rounded-lg px-3 py-2 text-sm border border-border outline-none w-36"
                  />
                </div>
                <div>
                  <label className="text-xs text-muted-foreground mb-1 block">In Stock</label>
                  <select
                    onChange={(e) => setPage(1)}
                    className="glass rounded-lg px-3 py-2 text-sm border border-border outline-none"
                  >
                    <option value="">All</option>
                    <option value="true">In Stock Only</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Category pills */}
          <div className="flex gap-2 flex-wrap">
            {CATEGORIES.map((cat) => (
              <button
                key={cat}
                onClick={() => { setSelectedCategory(cat); setPage(1); }}
                className={`px-3 py-1.5 rounded-full text-sm transition-all ${
                  selectedCategory === cat
                    ? "bg-primary text-primary-foreground"
                    : "glass border border-border hover:border-primary/30 text-muted-foreground hover:text-foreground"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Results count */}
        <div className="flex items-center justify-between mb-6">
          <p className="text-sm text-muted-foreground">
            {loading ? "Loading..." : `${total.toLocaleString()} products`}
            {selectedCategory !== "All" && <span> in <strong className="text-foreground">{selectedCategory}</strong></span>}
          </p>
          <Link
            href="/chat"
            className="flex items-center gap-2 text-sm text-primary hover:underline"
          >
            <Bot className="w-4 h-4" />
            Let AI help you find the perfect product
          </Link>
        </div>

        {/* Product Grid */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="glass rounded-2xl overflow-hidden">
                <div className="h-48 skeleton" />
                <div className="p-4 space-y-3">
                  <div className="h-4 skeleton rounded" />
                  <div className="h-3 skeleton rounded w-3/4" />
                  <div className="h-6 skeleton rounded w-1/2" />
                </div>
              </div>
            ))}
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-20">
            <Package className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No products found</h3>
            <p className="text-muted-foreground mb-6">Try different filters or ask the AI assistant</p>
            <Link href="/chat" className="flex items-center gap-2 mx-auto w-fit bg-primary text-primary-foreground px-6 py-3 rounded-xl">
              <Bot className="w-4 h-4" /> Ask AI Assistant
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {products.map((p) => (
              <ProductCard key={p.id} product={p} onAddToCart={handleAddToCart} />
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2 mt-12">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="glass p-2 rounded-lg disabled:opacity-50 hover:bg-card transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            {Array.from({ length: Math.min(7, totalPages) }, (_, i) => {
              const p = i + 1;
              return (
                <button
                  key={p}
                  onClick={() => setPage(p)}
                  className={`w-8 h-8 rounded-lg text-sm transition-all ${
                    page === p
                      ? "bg-primary text-primary-foreground"
                      : "glass hover:bg-card text-muted-foreground"
                  }`}
                >
                  {p}
                </button>
              );
            })}
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="glass p-2 rounded-lg disabled:opacity-50 hover:bg-card transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

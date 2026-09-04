"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import api, { type Product } from "@/lib/api";
import {
  Zap, Package, Plus, Search, Edit, Trash2, Loader2,
  ArrowLeft, ShoppingBag, LayoutGrid, CheckCircle2,
} from "lucide-react";
import { toast } from "@/components/ui/toaster";

export default function MerchantProducts() {
  const { isAuthenticated, isMerchant, isAdmin } = useAuth();
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [editingProduct, setEditingProduct] = useState<Partial<Product> | null>(null);

  useEffect(() => {
    if (!isAuthenticated) { router.push("/login?redirect=/merchant/products"); return; }
    if (!isMerchant && !isAdmin) { router.push("/"); return; }
    loadProducts();
  }, [isAuthenticated, isMerchant, isAdmin]);

  const loadProducts = async () => {
    try {
      const data = await api.getProducts({ page: 1, limit: 100 });
      setProducts(data.items);
    } catch (err) {
      toast({ title: "Failed", description: "Failed to load products", variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingProduct) return;
    try {
      if (editingProduct.id) {
        await api.updateProduct(editingProduct.id, editingProduct);
        toast({ title: "Product updated successfully" });
      } else {
        await api.createProduct(editingProduct);
        toast({ title: "Product created successfully" });
      }
      setEditingProduct(null);
      loadProducts();
    } catch (err) {
      toast({ title: "Failed", description: "Failed to save product", variant: "destructive" });
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this product?")) return;
    try {
      await api.deleteProduct(id);
      toast({ title: "Product deleted successfully" });
      loadProducts();
    } catch (err) {
      toast({ title: "Failed", description: "Failed to delete product", variant: "destructive" });
    }
  };

  const filteredProducts = products.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.category.toLowerCase().includes(search.toLowerCase())
  );

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
              <Link href="/merchant/products" className="text-primary font-medium">Products</Link>
            </nav>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">Product Catalog</h1>
            <p className="text-muted-foreground">Manage your AI-powered inventory</p>
          </div>
          <button
            onClick={() => setEditingProduct({ name: "", price: 0, stock: 1, is_active: true })}
            className="flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-violet-500 text-white px-5 py-2.5 rounded-xl font-medium hover:opacity-90 transition-opacity"
          >
            <Plus className="w-4 h-4" /> Add Product
          </button>
        </div>

        {editingProduct ? (
          <div className="glass rounded-2xl border border-border p-6 animate-slide-in">
            <div className="flex items-center gap-3 mb-6 border-b border-border pb-4">
              <button onClick={() => setEditingProduct(null)} className="p-2 hover:bg-secondary rounded-lg transition-colors">
                <ArrowLeft className="w-5 h-5 text-muted-foreground" />
              </button>
              <h2 className="text-xl font-bold">{editingProduct.id ? "Edit Product" : "New Product"}</h2>
            </div>
            <form onSubmit={handleSave} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">Product Name</label>
                  <input
                    type="text" required
                    value={editingProduct.name || ""}
                    onChange={e => setEditingProduct({...editingProduct, name: e.target.value})}
                    className="w-full bg-background border border-border rounded-xl px-4 py-2.5 focus:outline-none focus:border-primary/50"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">Category</label>
                  <input
                    type="text" required
                    value={editingProduct.category || ""}
                    onChange={e => setEditingProduct({...editingProduct, category: e.target.value})}
                    className="w-full bg-background border border-border rounded-xl px-4 py-2.5 focus:outline-none focus:border-primary/50"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">Price (₹)</label>
                  <input
                    type="number" required min="0" step="0.01"
                    value={editingProduct.price || 0}
                    onChange={e => setEditingProduct({...editingProduct, price: parseFloat(e.target.value)})}
                    className="w-full bg-background border border-border rounded-xl px-4 py-2.5 focus:outline-none focus:border-primary/50"
                  />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">Stock</label>
                  <input
                    type="number" required min="0"
                    value={editingProduct.stock || 0}
                    onChange={e => setEditingProduct({...editingProduct, stock: parseInt(e.target.value, 10)})}
                    className="w-full bg-background border border-border rounded-xl px-4 py-2.5 focus:outline-none focus:border-primary/50"
                  />
                </div>
              </div>
              <div className="flex gap-3 justify-end pt-4 border-t border-border">
                <button type="button" onClick={() => setEditingProduct(null)} className="px-5 py-2.5 rounded-xl hover:bg-secondary transition-colors font-medium">Cancel</button>
                <button type="submit" className="bg-primary text-primary-foreground px-5 py-2.5 rounded-xl font-medium hover:bg-primary/90 transition-colors">Save Product</button>
              </div>
            </form>
          </div>
        ) : (
          <div className="glass rounded-2xl border border-border overflow-hidden">
            <div className="p-4 border-b border-border bg-card/50 flex flex-col md:flex-row gap-4 justify-between items-center">
              <div className="relative w-full md:w-96">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search products..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  className="w-full bg-background border border-border rounded-xl pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-primary/50"
                />
              </div>
              <div className="text-sm text-muted-foreground whitespace-nowrap">
                {filteredProducts.length} items
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-border text-xs uppercase tracking-wider text-muted-foreground bg-secondary/30">
                    <th className="px-6 py-4 font-medium">Product</th>
                    <th className="px-6 py-4 font-medium">Category</th>
                    <th className="px-6 py-4 font-medium">Price</th>
                    <th className="px-6 py-4 font-medium">Stock</th>
                    <th className="px-6 py-4 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredProducts.map(product => (
                    <tr key={product.id} className="hover:bg-secondary/30 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center shrink-0">
                            <Package className="w-5 h-5 text-muted-foreground" />
                          </div>
                          <div>
                            <div className="font-medium text-sm text-foreground max-w-[200px] truncate">{product.name}</div>
                            <div className="text-xs text-muted-foreground">{product.brand}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary border border-primary/20">
                          {product.category}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-mono text-sm">
                        ₹{product.price.toLocaleString()}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1.5 text-xs font-medium ${product.stock > 10 ? 'text-emerald-400' : 'text-amber-400'}`}>
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          {product.stock}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button onClick={() => setEditingProduct(product)} className="p-2 hover:bg-primary/20 hover:text-primary rounded-lg transition-colors group">
                            <Edit className="w-4 h-4 text-muted-foreground group-hover:text-primary" />
                          </button>
                          <button onClick={() => handleDelete(product.id)} className="p-2 hover:bg-rose-500/20 hover:text-rose-400 rounded-lg transition-colors group">
                            <Trash2 className="w-4 h-4 text-muted-foreground group-hover:text-rose-400" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {filteredProducts.length === 0 && (
                    <tr>
                      <td colSpan={5} className="px-6 py-12 text-center text-muted-foreground">
                        No products found matching "{search}"
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

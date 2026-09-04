"""Seed script — 50+ products, demo users, seeded orders for analytics."""
from __future__ import annotations

import asyncio
import sys
import os
import uuid

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from datetime import UTC, datetime, timedelta
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./paypilot.db"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        print("🌱 Seeding PayPilot AI database...")
        await _seed_users(db)
        await _seed_products(db)
        await _seed_orders(db)
        print("✅ Seeding complete!")


async def _seed_users(db: AsyncSession) -> None:
    from app.core.security import hash_password
    from app.models import User, UserRole

    users = [
        {"name": "Demo Customer", "email": "customer@paypilot.demo", "role": UserRole.customer},
        {"name": "Demo Merchant", "email": "merchant@paypilot.demo", "role": UserRole.merchant},
        {"name": "Demo Admin", "email": "admin@paypilot.demo", "role": UserRole.admin},
    ]

    for u in users:
        result = await db.execute(
            text("SELECT id FROM users WHERE email = :email"), {"email": u["email"]}
        )
        if result.scalar_one_or_none():
            print(f"  ⏭ User {u['email']} already exists")
            continue
        user = User(
            name=u["name"],
            email=u["email"],
            password_hash=hash_password("Demo@123"),
            role=u["role"],
        )
        db.add(user)
        print(f"  ✓ Created user {u['email']}")

    await db.commit()


PRODUCTS = [
    # ── Smartphones ──────────────────────────────────────────────────────────
    {
        "name": "Samsung Galaxy S24 Ultra", "category": "Smartphones", "brand": "Samsung",
        "price": 129999, "original_price": 134999, "stock": 45, "rating": 4.7, "review_count": 2341,
        "description": "The Samsung Galaxy S24 Ultra features a 6.8-inch QHD+ Dynamic AMOLED display, Snapdragon 8 Gen 3, 200MP camera system, and built-in S Pen for productivity and creativity.",
        "tags": ["flagship", "camera", "s-pen", "5g", "android"],
        "features": ["200MP Main Camera", "12GB RAM", "256GB Storage", "5000mAh Battery", "S Pen Included", "IP68 Water Resistant"],
        "specifications": {"display": "6.8\" QHD+ AMOLED", "processor": "Snapdragon 8 Gen 3", "ram": "12GB", "storage": "256GB", "camera": "200MP+12MP+10MP+10MP", "battery": "5000mAh"},
        "image_url": "https://images.samsung.com/is/image/samsung/p6pim/in/2401/gallery/in-galaxy-s24-ultra-s928-sm-s928bzkcins-thumb-539573407",
    },
    {
        "name": "iPhone 15 Pro Max", "category": "Smartphones", "brand": "Apple",
        "price": 159900, "original_price": 164900, "stock": 32, "rating": 4.8, "review_count": 3102,
        "description": "Apple iPhone 15 Pro Max with A17 Pro chip, 48MP camera with 5x optical zoom, titanium design, and Action button. The most powerful iPhone ever.",
        "tags": ["flagship", "ios", "titanium", "5g", "camera", "apple"],
        "features": ["A17 Pro Chip", "48MP Main Camera", "5x Optical Zoom", "Titanium Frame", "USB-C", "Action Button"],
        "specifications": {"display": "6.7\" Super Retina XDR", "processor": "A17 Pro", "storage": "256GB", "camera": "48MP+12MP+12MP", "battery": "4422mAh"},
        "image_url": "https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/iphone-15-pro-max-black-titanium-select",
    },
    {
        "name": "OnePlus 12", "category": "Smartphones", "brand": "OnePlus",
        "price": 64999, "original_price": 69999, "stock": 67, "rating": 4.5, "review_count": 1456,
        "description": "OnePlus 12 powered by Snapdragon 8 Gen 3 with Hasselblad-tuned cameras, 100W SUPERVOOC charging, and 5400mAh battery. Premium flagship at competitive price.",
        "tags": ["flagship", "fast-charging", "hasselblad", "5g", "android"],
        "features": ["Snapdragon 8 Gen 3", "Hasselblad Camera", "100W SUPERVOOC", "5400mAh Battery", "LTPO 3.0 Display"],
        "specifications": {"display": "6.82\" LTPO AMOLED", "processor": "Snapdragon 8 Gen 3", "ram": "12GB", "storage": "256GB"},
        "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&q=80",
    },
    {
        "name": "Xiaomi 14 Pro", "category": "Smartphones", "brand": "Xiaomi",
        "price": 74999, "original_price": 79999, "stock": 54, "rating": 4.4, "review_count": 987,
        "description": "Xiaomi 14 Pro with Leica-tuned cameras, Snapdragon 8 Gen 3, ceramic body, and HyperOS. Professional photography meets flagship performance.",
        "tags": ["leica", "camera", "ceramic", "flagship", "5g"],
        "features": ["Leica Camera System", "Snapdragon 8 Gen 3", "Ceramic Back", "120W HyperCharge", "5000mAh Battery"],
        "specifications": {"display": "6.73\" LTPO AMOLED", "processor": "Snapdragon 8 Gen 3", "ram": "12GB"},
        "image_url": "https://images.unsplash.com/photo-1567581935884-3349723552ca?w=600&q=80",
    },
    {
        "name": "Realme 12 Pro+", "category": "Smartphones", "brand": "Realme",
        "price": 29999, "original_price": 34999, "stock": 89, "rating": 4.3, "review_count": 1234,
        "description": "Realme 12 Pro+ with periscope camera (3x optical zoom), Dimensity 7050, and slim curved design. Mid-range powerhouse with flagship camera features.",
        "tags": ["mid-range", "periscope", "camera", "5g"],
        "features": ["64MP Periscope Camera", "Dimensity 7050", "67W SUPERVOOC", "5000mAh Battery"],
        "specifications": {"display": "6.67\" AMOLED", "processor": "Dimensity 7050", "ram": "8GB"},
        "image_url": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600&q=80",
    },
    # ── Laptops ──────────────────────────────────────────────────────────────
    {
        "name": "MacBook Pro 14 M3 Pro", "category": "Laptops", "brand": "Apple",
        "price": 199900, "original_price": 209900, "stock": 28, "rating": 4.9, "review_count": 1876,
        "description": "MacBook Pro 14 with M3 Pro chip delivers extraordinary performance for professional workflows including video editing, 3D rendering, and software development.",
        "tags": ["professional", "m3", "macos", "programming", "video-editing", "design"],
        "features": ["M3 Pro Chip", "18GB Unified Memory", "512GB SSD", "18-hour Battery", "MiniLED Display", "Thunderbolt 4"],
        "specifications": {"display": "14.2\" Liquid Retina XDR", "processor": "Apple M3 Pro", "ram": "18GB", "storage": "512GB SSD"},
        "image_url": "https://store.storeimages.cdn-apple.com/4668/as-images.apple.com/is/mbp14-spacegray-select-202310",
    },
    {
        "name": "ASUS ROG Zephyrus G14", "category": "Laptops", "brand": "ASUS",
        "price": 149990, "original_price": 159990, "stock": 22, "rating": 4.6, "review_count": 987,
        "description": "ASUS ROG Zephyrus G14 gaming laptop with AMD Ryzen 9, RTX 4070, and AniMe Matrix LED lid. The ultimate gaming ultrabook that can do it all.",
        "tags": ["gaming", "rtx4070", "ultrabook", "amd", "portable"],
        "features": ["AMD Ryzen 9 8945HS", "RTX 4070 8GB", "16GB DDR5", "1TB NVMe SSD", "AniMe Matrix Display", "165Hz QHD+"],
        "specifications": {"display": "14\" QHD+ 165Hz", "processor": "Ryzen 9 8945HS", "gpu": "RTX 4070", "ram": "16GB", "storage": "1TB SSD"},
        "image_url": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=600&q=80",
    },
    {
        "name": "Dell XPS 15 (2024)", "category": "Laptops", "brand": "Dell",
        "price": 179990, "original_price": 189990, "stock": 18, "rating": 4.7, "review_count": 654,
        "description": "Dell XPS 15 with Intel Core Ultra 9, RTX 4070 Max-Q, and stunning OLED display. The perfect blend of performance and elegance for creative professionals.",
        "tags": ["professional", "oled", "programming", "creative", "windows"],
        "features": ["Intel Core Ultra 9", "RTX 4070 Max-Q", "32GB RAM", "1TB SSD", "OLED Touch Display", "Thunderbolt 4"],
        "specifications": {"display": "15.6\" OLED Touch", "processor": "Intel Core Ultra 9", "ram": "32GB", "storage": "1TB SSD"},
        "image_url": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&q=80",
    },
    {
        "name": "HP Pavilion 15 (Ryzen 5)", "category": "Laptops", "brand": "HP",
        "price": 54990, "original_price": 64990, "stock": 56, "rating": 4.2, "review_count": 2341,
        "description": "HP Pavilion 15 with AMD Ryzen 5, Full HD display, and long battery life. The perfect everyday laptop for students and professionals on a budget.",
        "tags": ["budget", "student", "everyday", "programming", "office"],
        "features": ["AMD Ryzen 5 7530U", "16GB RAM", "512GB SSD", "10-hour Battery", "Full HD Display", "Fingerprint Reader"],
        "specifications": {"display": "15.6\" FHD", "processor": "Ryzen 5 7530U", "ram": "16GB", "storage": "512GB SSD"},
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&q=80",
    },
    {
        "name": "Lenovo ThinkPad X1 Carbon", "category": "Laptops", "brand": "Lenovo",
        "price": 139990, "original_price": 149990, "stock": 34, "rating": 4.8, "review_count": 1102,
        "description": "Lenovo ThinkPad X1 Carbon Gen 12 — the iconic business ultrabook with Intel Core Ultra, military-grade durability, and legendary keyboard. Built for professionals.",
        "tags": ["business", "ultrabook", "durable", "programming", "office"],
        "features": ["Intel Core Ultra 7", "16GB LPDDR5X", "512GB SSD", "Wi-Fi 6E", "IR Camera", "Backlit Keyboard"],
        "specifications": {"display": "14\" 2.8K OLED", "processor": "Intel Core Ultra 7", "ram": "16GB", "storage": "512GB"},
        "image_url": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=600&q=80",
    },
    # ── Headphones ────────────────────────────────────────────────────────────
    {
        "name": "Sony WH-1000XM5", "category": "Headphones", "brand": "Sony",
        "price": 29990, "original_price": 34990, "stock": 78, "rating": 4.8, "review_count": 4523,
        "description": "Sony WH-1000XM5 — industry-leading noise cancellation, 30-hour battery, crystal-clear call quality. The gold standard in premium wireless headphones.",
        "tags": ["noise-cancelling", "wireless", "music", "travel", "premium", "over-ear"],
        "features": ["Industry-Leading ANC", "30hr Battery", "Multipoint Connection", "Speak-to-Chat", "360 Audio", "Foldable Design"],
        "specifications": {"type": "Over-ear", "connectivity": "Bluetooth 5.2", "battery": "30 hours", "anc": "Yes"},
        "image_url": "https://www.sony.co.in/image/5d02da5df552836db894cead8a68f764?fmt=pjpeg",
        "cross_sell_ids": [],  # Will be set after product IDs are known
    },
    {
        "name": "Bose QuietComfort 45", "category": "Headphones", "brand": "Bose",
        "price": 24990, "original_price": 32990, "stock": 65, "rating": 4.7, "review_count": 3234,
        "description": "Bose QC45 delivers legendary Bose noise cancellation in a lightweight, comfortable design. Perfect for long listening sessions and frequent travelers.",
        "tags": ["noise-cancelling", "wireless", "music", "travel", "comfort"],
        "features": ["Bose ANC", "24hr Battery", "Aware Mode", "USB-C", "Foldable", "Premium Build"],
        "specifications": {"type": "Over-ear", "connectivity": "Bluetooth 5.1", "battery": "24 hours"},
        "image_url": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&q=80",
    },
    {
        "name": "boAt Rockerz 550", "category": "Headphones", "brand": "boAt",
        "price": 1799, "original_price": 3990, "stock": 234, "rating": 4.1, "review_count": 18234,
        "description": "boAt Rockerz 550 wireless headphones with 20-hour battery, 40mm drivers, and foldable design. Excellent value for money everyday headphones.",
        "tags": ["budget", "wireless", "everyday", "bass"],
        "features": ["20hr Battery", "40mm Drivers", "Foldable", "Voice Assistant Support", "USB-C Charging"],
        "specifications": {"type": "Over-ear", "connectivity": "Bluetooth 5.0", "battery": "20 hours"},
        "image_url": "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=600&q=80",
    },
    {
        "name": "Sony WH-1000XM4", "category": "Headphones", "brand": "Sony",
        "price": 24990, "original_price": 29990, "stock": 89, "rating": 4.7, "review_count": 5678,
        "description": "Sony WH-1000XM4 — previous generation flagship with outstanding ANC, 30-hour battery, and multipoint connection. Excellent at its reduced price.",
        "tags": ["noise-cancelling", "wireless", "music", "travel"],
        "features": ["ANC", "30hr Battery", "Multipoint", "Speak-to-Chat", "Google Assistant"],
        "specifications": {"type": "Over-ear", "connectivity": "Bluetooth 5.0", "battery": "30 hours"},
        "image_url": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=600&q=80",
    },
    {
        "name": "JBL Quantum 360 Gaming", "category": "Headphones", "brand": "JBL",
        "price": 7999, "original_price": 9999, "stock": 112, "rating": 4.3, "review_count": 2341,
        "description": "JBL Quantum 360 wireless gaming headset with JBL QuantumSurround sound, detachable boom mic, and 22-hour battery. Your gaming advantage.",
        "tags": ["gaming", "wireless", "surround-sound", "microphone"],
        "features": ["JBL QuantumSurround", "22hr Battery", "Detachable Mic", "2.4GHz+Bluetooth", "PS/Xbox/PC"],
        "specifications": {"type": "Over-ear", "connectivity": "2.4GHz + Bluetooth", "battery": "22 hours", "mic": "Detachable boom"},
        "image_url": "https://images.unsplash.com/photo-1612444530582-fc66183b16f7?w=600&q=80",
    },
    # ── Gaming ────────────────────────────────────────────────────────────────
    {
        "name": "Razer DeathAdder V3 Pro", "category": "Gaming", "sub_category": "Mice",
        "brand": "Razer", "price": 12999, "original_price": 14999, "stock": 89,
        "rating": 4.6, "review_count": 1876,
        "description": "Razer DeathAdder V3 Pro — ultra-lightweight wireless gaming mouse with 30K DPI optical sensor, 90-hour battery, and ergonomic design for right-handers.",
        "tags": ["gaming", "mouse", "wireless", "ergonomic", "fps"],
        "features": ["30K DPI Sensor", "90hr Battery", "63g Ultra-Light", "HyperSpeed Wireless", "HyperPolling 4000Hz"],
        "specifications": {"dpi": "100-30000", "weight": "63g", "buttons": "8", "battery": "90 hours"},
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&q=80",
    },
    {
        "name": "Logitech G Pro X Superlight 2", "category": "Gaming", "sub_category": "Mice",
        "brand": "Logitech", "price": 11999, "original_price": 13999, "stock": 67,
        "rating": 4.7, "review_count": 2341,
        "description": "Logitech G Pro X Superlight 2 — HERO 25K sensor, 60g ultra-lightweight design, LightSpeed wireless. The choice of professional esports players.",
        "tags": ["gaming", "mouse", "wireless", "pro", "fps", "esports"],
        "features": ["HERO 25K Sensor", "60g Ultra-Light", "LightSpeed Wireless", "95hr Battery", "Zero Clicks"],
        "specifications": {"dpi": "100-25600", "weight": "60g", "buttons": "5", "battery": "95 hours"},
        "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&q=80",
    },
    {
        "name": "Corsair K100 RGB Mechanical", "category": "Gaming", "sub_category": "Keyboards",
        "brand": "Corsair", "price": 18999, "original_price": 22999, "stock": 45,
        "rating": 4.5, "review_count": 1234,
        "description": "Corsair K100 RGB — OPX optical-mechanical switches, per-key RGB, programmable macro wheel, and iCUE software integration. The pinnacle of mechanical keyboards.",
        "tags": ["gaming", "keyboard", "mechanical", "rgb", "optical"],
        "features": ["OPX Optical Switches", "Per-key RGB", "Macro Wheel", "USB Type-A Passthrough", "iCUE Software"],
        "specifications": {"switch": "OPX Optical-Mechanical", "layout": "Full-size", "connectivity": "Wired USB"},
        "image_url": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=600&q=80",
    },
    {
        "name": "ASUS ROG Swift 27\" 360Hz", "category": "Gaming", "sub_category": "Monitors",
        "brand": "ASUS", "price": 64999, "original_price": 74999, "stock": 23,
        "rating": 4.6, "review_count": 567,
        "description": "ASUS ROG Swift PG27AQN — 27\" QHD 360Hz IPS display with G-Sync Ultimate, 1ms response time, and ROG SWIFT lighting. Competitive gaming at its finest.",
        "tags": ["gaming", "monitor", "360hz", "gsync", "competitive"],
        "features": ["360Hz Refresh Rate", "G-Sync Ultimate", "1ms Response", "QHD 2560x1440", "HDR600", "Adjustable Stand"],
        "specifications": {"size": "27\"", "resolution": "2560x1440", "refresh_rate": "360Hz", "panel": "IPS"},
        "image_url": "https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=600&q=80",
    },
    {
        "name": "PlayStation 5 DualSense Controller", "category": "Gaming", "sub_category": "Controllers",
        "brand": "Sony", "price": 5990, "original_price": 6490, "stock": 145,
        "rating": 4.8, "review_count": 5432,
        "description": "Sony DualSense Wireless Controller for PS5 with haptic feedback, adaptive triggers, and built-in microphone. Revolutionary immersive gaming experience.",
        "tags": ["gaming", "controller", "ps5", "haptic", "wireless"],
        "features": ["Haptic Feedback", "Adaptive Triggers", "Built-in Mic", "USB-C Charging", "12hr Battery"],
        "specifications": {"compatibility": "PS5, PC", "connectivity": "Bluetooth", "battery": "12 hours"},
        "image_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=600&q=80",
    },
    # ── Cameras ───────────────────────────────────────────────────────────────
    {
        "name": "Sony Alpha A7 IV", "category": "Cameras", "brand": "Sony",
        "price": 259990, "original_price": 274990, "stock": 15, "rating": 4.8, "review_count": 876,
        "description": "Sony Alpha A7 IV — 33MP full-frame BSI-CMOS sensor, AI-powered autofocus, 4K 60fps video, and professional-grade build. The ultimate hybrid camera.",
        "tags": ["fullframe", "mirrorless", "professional", "photography", "video", "4k"],
        "features": ["33MP Full-Frame Sensor", "AI AF System", "4K 60fps", "Real-Time Eye AF", "5-Axis IBIS", "Dual Card Slots"],
        "specifications": {"sensor": "33MP Full-Frame", "autofocus": "759-point AI", "video": "4K 60fps", "iso": "100-51200"},
        "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&q=80",
    },
    {
        "name": "Canon EOS R50", "category": "Cameras", "brand": "Canon",
        "price": 64990, "original_price": 74990, "stock": 34, "rating": 4.5, "review_count": 654,
        "description": "Canon EOS R50 — 24MP APS-C sensor, dual pixel autofocus, 4K 30fps video, and compact body. The perfect beginner mirrorless for photography enthusiasts.",
        "tags": ["beginner", "mirrorless", "4k", "apsc", "photography"],
        "features": ["24MP APS-C Sensor", "Dual Pixel AF", "4K 30fps", "Vari-Angle LCD", "Wi-Fi+Bluetooth", "Compact Body"],
        "specifications": {"sensor": "24MP APS-C", "autofocus": "Dual Pixel CMOS AF II", "video": "4K 30fps"},
        "image_url": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=600&q=80",
    },
    {
        "name": "GoPro Hero 12 Black", "category": "Cameras", "brand": "GoPro",
        "price": 39990, "original_price": 44990, "stock": 56, "rating": 4.6, "review_count": 2341,
        "description": "GoPro Hero 12 Black — 5.3K 60fps, HyperSmooth 6.0 stabilization, HDR video, and Enduro battery for longer shoots in any condition.",
        "tags": ["action", "waterproof", "4k", "sports", "travel", "vlog"],
        "features": ["5.3K 60fps Video", "HyperSmooth 6.0", "HDR Video", "Waterproof 10m", "Enduro Battery", "Bluetooth Remote"],
        "specifications": {"video": "5.3K 60fps", "stabilization": "HyperSmooth 6.0", "waterproof": "10m"},
        "image_url": "https://images.unsplash.com/photo-1499892477393-f675706cbe6e?w=600&q=80",
    },
    # ── Smartwatches ──────────────────────────────────────────────────────────
    {
        "name": "Apple Watch Series 9 45mm", "category": "Smartwatches", "brand": "Apple",
        "price": 44900, "original_price": 47900, "stock": 67, "rating": 4.7, "review_count": 2341,
        "description": "Apple Watch Series 9 with S9 SiP chip, brighter always-on display, double tap gesture, and advanced health tracking including ECG and blood oxygen.",
        "tags": ["smartwatch", "health", "fitness", "ios", "apple"],
        "features": ["S9 SiP Chip", "Always-On Display", "ECG App", "Blood Oxygen", "Crash Detection", "18hr Battery"],
        "specifications": {"display": "1.9\" LTPO OLED", "compatibility": "iPhone", "battery": "18 hours", "waterproof": "50m"},
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80",
    },
    {
        "name": "Samsung Galaxy Watch 6 Classic", "category": "Smartwatches", "brand": "Samsung",
        "price": 32999, "original_price": 36999, "stock": 89, "rating": 4.5, "review_count": 1456,
        "description": "Samsung Galaxy Watch 6 Classic with rotating bezel, advanced sleep coaching, body composition analysis, and 40-hour battery life.",
        "tags": ["smartwatch", "health", "fitness", "android", "rotating-bezel"],
        "features": ["Rotating Bezel", "Advanced Sleep Tracking", "Body Composition", "BioActive Sensor", "40hr Battery"],
        "specifications": {"display": "1.5\" AMOLED", "compatibility": "Android", "battery": "40 hours"},
        "image_url": "https://images.unsplash.com/photo-1617043786394-f977fa12eddf?w=600&q=80",
    },
    {
        "name": "boAt Wave Sigma 2 Pro", "category": "Smartwatches", "brand": "boAt",
        "price": 1799, "original_price": 4999, "stock": 456, "rating": 4.0, "review_count": 12341,
        "description": "boAt Wave Sigma 2 Pro with 1.85\" HD display, Bluetooth calling, 100+ sports modes, and 7-day battery. Incredible value budget smartwatch.",
        "tags": ["budget", "smartwatch", "bluetooth-calling", "fitness"],
        "features": ["1.85\" HD Display", "Bluetooth Calling", "100+ Sports Modes", "7-day Battery", "IP67"],
        "specifications": {"display": "1.85\" TFT", "battery": "7 days", "waterproof": "IP67"},
        "image_url": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=600&q=80",
    },
    # ── Tablets ───────────────────────────────────────────────────────────────
    {
        "name": "iPad Pro 12.9\" M4", "category": "Tablets", "brand": "Apple",
        "price": 109900, "original_price": 119900, "stock": 34, "rating": 4.9, "review_count": 1234,
        "description": "iPad Pro 12.9\" with M4 chip, Ultra Retina XDR OLED display, Apple Pencil Pro support, and WiFi 6E. The most powerful iPad ever created.",
        "tags": ["tablet", "ipad", "m4", "professional", "creative", "apple-pencil"],
        "features": ["M4 Chip", "Ultra Retina XDR OLED", "Apple Pencil Pro", "Wi-Fi 6E", "Liquid Retina XDR", "10hr Battery"],
        "specifications": {"display": "12.9\" Ultra Retina XDR OLED", "processor": "Apple M4", "storage": "256GB"},
        "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600&q=80",
    },
    {
        "name": "Samsung Galaxy Tab S9 FE", "category": "Tablets", "brand": "Samsung",
        "price": 39999, "original_price": 44999, "stock": 78, "rating": 4.4, "review_count": 987,
        "description": "Samsung Galaxy Tab S9 FE with 10.9\" LCD, Exynos 1380, S Pen included, and IP68 water resistance. A capable mid-range Android tablet.",
        "tags": ["tablet", "android", "s-pen", "waterproof", "samsung"],
        "features": ["S Pen Included", "IP68", "8000mAh Battery", "Quad Speaker", "Samsung DeX Support"],
        "specifications": {"display": "10.9\" TFT LCD", "processor": "Exynos 1380", "storage": "128GB"},
        "image_url": "https://images.unsplash.com/photo-1589739900243-4b52cd9b104e?w=600&q=80",
    },
    # ── Laptop Accessories ────────────────────────────────────────────────────
    {
        "name": "Logitech MX Master 3S", "category": "Laptop Accessories", "sub_category": "Mice",
        "brand": "Logitech", "price": 9995, "original_price": 11995, "stock": 123,
        "rating": 4.7, "review_count": 3456,
        "description": "Logitech MX Master 3S — the gold standard of productivity mice. 8K DPI sensor, electromagnetic scroll wheel, multi-device support, and 70-day battery.",
        "tags": ["productivity", "wireless", "ergonomic", "office", "programming"],
        "features": ["8K DPI Sensor", "MagSpeed Scroll", "Multi-Device", "USB-C", "70-day Battery", "Quiet Clicks"],
        "specifications": {"dpi": "200-8000", "connectivity": "Bluetooth + Logi Bolt", "battery": "70 days"},
        "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&q=80",
    },
    {
        "name": "Logitech MX Keys Mini", "category": "Laptop Accessories", "sub_category": "Keyboards",
        "brand": "Logitech", "price": 7995, "original_price": 9995, "stock": 89,
        "rating": 4.5, "review_count": 2134,
        "description": "Logitech MX Keys Mini compact wireless keyboard with smart illumination, scissor switches, and multi-device pairing. Perfectly paired with MX Master.",
        "tags": ["productivity", "wireless", "compact", "office", "programming", "backlit"],
        "features": ["Backlit Keys", "Smart Illumination", "Multi-Device", "USB-C", "10-day Battery"],
        "specifications": {"connectivity": "Bluetooth + Logi Bolt", "layout": "TKL", "battery": "10 days"},
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&q=80",
    },
    {
        "name": "Dell 27\" 4K USB-C Monitor", "category": "Laptop Accessories", "sub_category": "Monitors",
        "brand": "Dell", "price": 44990, "original_price": 52990, "stock": 34,
        "rating": 4.6, "review_count": 876,
        "description": "Dell U2723D 4K USB-C monitor with 96W power delivery, IPS Black panel, and factory-calibrated color accuracy. Perfect for creative professionals.",
        "tags": ["monitor", "4k", "usb-c", "professional", "creative"],
        "features": ["4K IPS Black Panel", "96W USB-C PD", "99% sRGB", "Factory Calibrated", "PbP/PiP"],
        "specifications": {"resolution": "3840x2160", "panel": "IPS Black", "refresh_rate": "60Hz", "hdr": "HDR400"},
        "image_url": "https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=600&q=80",
    },
    {
        "name": "Targus 15.6\" Laptop Bag", "category": "Laptop Accessories", "sub_category": "Bags",
        "brand": "Targus", "price": 2499, "original_price": 3999, "stock": 234,
        "rating": 4.3, "review_count": 4567,
        "description": "Targus 15.6\" laptop bag with padded laptop compartment, multiple organizer pockets, and water-resistant material. Professional and practical.",
        "tags": ["bag", "laptop-bag", "15-inch", "office", "travel"],
        "features": ["Padded Laptop Section", "Multiple Pockets", "Water Resistant", "Padded Shoulder Strap"],
        "specifications": {"fits": "Up to 15.6\"", "material": "Polyester", "weight": "0.8kg"},
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&q=80",
    },
    # ── Phone Accessories ─────────────────────────────────────────────────────
    {
        "name": "Anker 65W 3-Port USB-C Charger", "category": "Phone Cases", "sub_category": "Chargers",
        "brand": "Anker", "price": 2799, "original_price": 3499, "stock": 345,
        "rating": 4.7, "review_count": 6789,
        "description": "Anker 65W GaN charger with 3 ports (2x USB-C + 1x USB-A), PowerIQ 4.0, and compact design. Charge your laptop, phone, and tablet simultaneously.",
        "tags": ["charger", "gan", "usb-c", "fast-charging", "travel"],
        "features": ["65W Total Power", "GaN Technology", "3 Ports", "PowerIQ 4.0", "Compact Design"],
        "specifications": {"power": "65W", "ports": "2x USB-C + 1x USB-A", "compatibility": "Universal"},
        "image_url": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&q=80",
    },
    {
        "name": "Spigen Ultra Hybrid iPhone 15 Case", "category": "Phone Cases", "sub_category": "Cases",
        "brand": "Spigen", "price": 1299, "original_price": 1999, "stock": 456,
        "rating": 4.5, "review_count": 12341,
        "description": "Spigen Ultra Hybrid iPhone 15 case with crystal-clear back, air cushion corners, and military-grade drop protection. Show off your phone while keeping it safe.",
        "tags": ["case", "iphone15", "clear", "protection"],
        "features": ["Military-Grade Protection", "Crystal Clear Back", "Air Cushion Corners", "Wireless Charging Compatible"],
        "specifications": {"compatibility": "iPhone 15", "material": "PC + TPU"},
        "image_url": "https://images.unsplash.com/photo-1601593346740-925612772716?w=600&q=80",
    },
    # ── Speakers ──────────────────────────────────────────────────────────────
    {
        "name": "JBL Charge 5", "category": "Speakers", "brand": "JBL",
        "price": 14999, "original_price": 16999, "stock": 89, "rating": 4.6, "review_count": 3456,
        "description": "JBL Charge 5 portable Bluetooth speaker with IP67 waterproof rating, 20-hour battery, and powerbank functionality. Massive sound for outdoor adventures.",
        "tags": ["speaker", "bluetooth", "waterproof", "portable", "outdoor"],
        "features": ["IP67 Waterproof", "20hr Battery", "PartyBoost", "USB-C Charging", "Powerbank Output"],
        "specifications": {"connectivity": "Bluetooth 5.1", "battery": "20 hours", "waterproof": "IP67"},
        "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&q=80",
    },
    {
        "name": "Sony SRS-XB33", "category": "Speakers", "brand": "Sony",
        "price": 9990, "original_price": 12990, "stock": 112, "rating": 4.4, "review_count": 2134,
        "description": "Sony SRS-XB33 with Extra Bass, party lighting, IP67 waterproof, and 24-hour battery. Bring the party anywhere.",
        "tags": ["speaker", "bluetooth", "waterproof", "bass", "party"],
        "features": ["Extra Bass", "Party Lighting", "IP67", "24hr Battery", "Party Connect"],
        "specifications": {"connectivity": "Bluetooth 5.0", "battery": "24 hours", "waterproof": "IP67"},
        "image_url": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&q=80",
    },
    # ── Camera Accessories ────────────────────────────────────────────────────
    {
        "name": "SanDisk 128GB Extreme Pro SD Card", "category": "Camera Accessories",
        "brand": "SanDisk", "price": 2499, "original_price": 3499, "stock": 567,
        "rating": 4.7, "review_count": 8901,
        "description": "SanDisk Extreme Pro 128GB UHS-I SD card with 200MB/s read and 90MB/s write speed. Perfect for 4K video and burst photography.",
        "tags": ["memory-card", "sdcard", "4k", "camera", "128gb"],
        "features": ["200MB/s Read", "90MB/s Write", "4K UHD Video", "V30 / U3 / Class 10", "Shock+Temperature Proof"],
        "specifications": {"capacity": "128GB", "speed_class": "V30/U3/Class 10", "read": "200MB/s", "write": "90MB/s"},
        "image_url": "https://images.unsplash.com/photo-1618424181497-157f25b6ddd5?w=600&q=80",
    },
    {
        "name": "Joby GorillaPod 3K Kit", "category": "Camera Accessories",
        "brand": "Joby", "price": 5499, "original_price": 6999, "stock": 89,
        "rating": 4.5, "review_count": 1234,
        "description": "Joby GorillaPod 3K — flexible, lightweight tripod that wraps around poles, hangs from branches, or stands on uneven surfaces. 3kg payload for mirrorless cameras.",
        "tags": ["tripod", "gorilla-pod", "flexible", "portable", "mirrorless"],
        "features": ["3kg Payload", "Flexible Legs", "Ball Head", "Magnetic Feet", "Lightweight 485g"],
        "specifications": {"payload": "3kg", "weight": "485g", "material": "ABS+TPE"},
        "image_url": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&q=80",
    },
    # ── More Gaming ───────────────────────────────────────────────────────────
    {
        "name": "Razer BlackShark V2 Pro", "category": "Headphones", "brand": "Razer",
        "price": 14999, "original_price": 17999, "stock": 67, "rating": 4.5, "review_count": 1876,
        "description": "Razer BlackShark V2 Pro — THX Spatial Audio, HyperClear microphone, 70-hour battery, and HyperSpeed wireless. The pro esports gaming headset.",
        "tags": ["gaming", "wireless", "headset", "microphone", "esports", "thx"],
        "features": ["THX Spatial Audio", "HyperClear Mic", "70hr Battery", "HyperSpeed 2.4GHz", "Titanium Drivers"],
        "specifications": {"connectivity": "HyperSpeed 2.4GHz", "battery": "70 hours", "mic": "Detachable HyperClear"},
        "image_url": "https://images.unsplash.com/photo-1612444530582-fc66183b16f7?w=600&q=80",
    },
    {
        "name": "HyperX Cloud Alpha Wireless", "category": "Headphones", "brand": "HyperX",
        "price": 12999, "original_price": 14999, "stock": 89, "rating": 4.4, "review_count": 1345,
        "description": "HyperX Cloud Alpha Wireless gaming headset with 300-hour battery life, DTS Headphone:X, and dual-chamber drivers. The longest-lasting wireless gaming headset.",
        "tags": ["gaming", "wireless", "headset", "300hr-battery"],
        "features": ["300hr Battery", "DTS Headphone:X", "Dual-Chamber Drivers", "Detachable Mic", "2.4GHz Wireless"],
        "specifications": {"connectivity": "2.4GHz USB", "battery": "300 hours"},
        "image_url": "https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=600&q=80",
    },
    # ── Earbuds ───────────────────────────────────────────────────────────────
    {
        "name": "Sony WF-1000XM5", "category": "Headphones", "sub_category": "Earbuds",
        "brand": "Sony", "price": 24990, "original_price": 29990, "stock": 89,
        "rating": 4.7, "review_count": 2341,
        "description": "Sony WF-1000XM5 — the world's best ANC earbuds with QN2e processor, 8hr battery (+16hr case), and crystal-clear call quality.",
        "tags": ["earbuds", "anc", "wireless", "premium", "tws"],
        "features": ["World's Best ANC", "8hr+16hr Battery", "Hi-Res Audio", "Crystal-Clear Calls", "IPX4"],
        "specifications": {"type": "TWS Earbuds", "anc": "Industry Leading", "battery": "8+16 hours", "charging": "USB-C + Wireless"},
        "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&q=80",
    },
    {
        "name": "boAt Airdopes 141", "category": "Headphones", "sub_category": "Earbuds",
        "brand": "boAt", "price": 999, "original_price": 2990, "stock": 789,
        "rating": 4.0, "review_count": 45678,
        "description": "boAt Airdopes 141 — budget TWS earbuds with 6hr battery (+30hr case), beast mode for gaming, and IPX4 water resistance. Best-selling budget earbuds.",
        "tags": ["earbuds", "budget", "tws", "wireless", "gaming-mode"],
        "features": ["6+30hr Battery", "Beast Mode", "IPX4", "Dual Mic", "ASAP Charge"],
        "specifications": {"type": "TWS Earbuds", "battery": "6+30 hours", "waterproof": "IPX4"},
        "image_url": "https://images.unsplash.com/photo-1606220838315-056192d5e927?w=600&q=80",
    },
    # ── More laptops ──────────────────────────────────────────────────────────
    {
        "name": "Acer Nitro V 15 Gaming", "category": "Laptops", "brand": "Acer",
        "price": 69990, "original_price": 79990, "stock": 34, "rating": 4.3, "review_count": 1234,
        "description": "Acer Nitro V 15 gaming laptop with RTX 4060, Ryzen 7, 16GB RAM, and 144Hz display. Get into gaming without breaking the bank.",
        "tags": ["gaming", "rtx4060", "budget-gaming", "student"],
        "features": ["RTX 4060 8GB", "Ryzen 7 7745HX", "16GB DDR5", "512GB NVMe", "144Hz FHD Display"],
        "specifications": {"display": "15.6\" FHD 144Hz", "gpu": "RTX 4060", "processor": "Ryzen 7 7745HX"},
        "image_url": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=600&q=80",
    },
    {
        "name": "HP Spectre x360 14", "category": "Laptops", "brand": "HP",
        "price": 159990, "original_price": 169990, "stock": 23, "rating": 4.7, "review_count": 678,
        "description": "HP Spectre x360 14 convertible laptop with Intel Core Ultra 7, OLED touch display, and 360° hinge. Luxury performance for creative professionals.",
        "tags": ["convertible", "oled", "touch", "premium", "professional", "2-in-1"],
        "features": ["Intel Core Ultra 7", "OLED Touch Display", "360° Hinge", "18hr Battery", "Thunderbolt 4", "Pen Support"],
        "specifications": {"display": "14\" 2.8K OLED OLED 120Hz", "processor": "Intel Core Ultra 7"},
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&q=80",
    },
]


async def _seed_products(db: AsyncSession) -> None:
    from app.models import Product

    existing = await db.execute(text("SELECT COUNT(*) FROM products"))
    count = existing.scalar_one()
    if count > 0:
        print(f"  ⏭ Products already seeded ({count} products)")
        return

    product_objects = []
    for p_data in PRODUCTS:
        product = Product(**p_data)
        db.add(product)
        product_objects.append(product)
        print(f"  ✓ Product: {p_data['name']}")

    await db.flush()

    # Now set cross-sell and upsell relationships
    # Get products by category
    result = await db.execute(text("SELECT id, name, category, sub_category, price FROM products"))
    all_products = {row.name: {"id": row.id, "category": row.category, "price": float(row.price)} for row in result.all()}

    # Set some cross-sell relationships
    cross_sells = {
        "Sony WH-1000XM5": ["Anker 65W 3-Port USB-C Charger"],
        "JBL Quantum 360 Gaming": ["Razer DeathAdder V3 Pro", "Corsair K100 RGB Mechanical"],
        "MacBook Pro 14 M3 Pro": ["Logitech MX Master 3S", "Logitech MX Keys Mini", "Dell 27\" 4K USB-C Monitor", "Targus 15.6\" Laptop Bag"],
        "ASUS ROG Zephyrus G14": ["Razer DeathAdder V3 Pro", "JBL Quantum 360 Gaming", "Corsair K100 RGB Mechanical"],
        "iPhone 15 Pro Max": ["Spigen Ultra Hybrid iPhone 15 Case", "Anker 65W 3-Port USB-C Charger", "Apple Watch Series 9 45mm"],
        "Samsung Galaxy S24 Ultra": ["Anker 65W 3-Port USB-C Charger", "Samsung Galaxy Watch 6 Classic"],
        "Sony Alpha A7 IV": ["SanDisk 128GB Extreme Pro SD Card", "Joby GorillaPod 3K Kit"],
        "Canon EOS R50": ["SanDisk 128GB Extreme Pro SD Card", "Joby GorillaPod 3K Kit"],
    }

    for prod_name, cs_names in cross_sells.items():
        prod_result = await db.execute(
            text("SELECT id FROM products WHERE name = :name"), {"name": prod_name}
        )
        prod_id = prod_result.scalar_one_or_none()
        if not prod_id:
            continue
        cs_ids = []
        for cs_name in cs_names:
            cs_result = await db.execute(
                text("SELECT id FROM products WHERE name = :name"), {"name": cs_name}
            )
            cs_id = cs_result.scalar_one_or_none()
            if cs_id:
                cs_ids.append(cs_id)
        if cs_ids:
            await db.execute(
                text("UPDATE products SET cross_sell_ids = :ids WHERE id = :prod_id"),
                {"ids": str(cs_ids).replace("'", '"'), "prod_id": prod_id}
            )

    await db.commit()
    print(f"  ✅ Seeded {len(PRODUCTS)} products")


async def _seed_orders(db: AsyncSession) -> None:
    """Seed realistic demo orders for analytics dashboard."""
    from datetime import UTC, datetime, timedelta
    import random

    existing = await db.execute(text("SELECT COUNT(*) FROM orders WHERE status != 'draft'"))
    count = existing.scalar_one()
    if count > 10:
        print(f"  ⏭ Orders already seeded ({count} orders)")
        return

    # Get customer user ID
    result = await db.execute(text("SELECT id FROM users WHERE email = 'customer@paypilot.demo'"))
    customer_id = result.scalar_one_or_none()
    if not customer_id:
        return

    # Get some product IDs and prices
    prod_result = await db.execute(text("SELECT id, price FROM products WHERE is_active = true LIMIT 20"))
    products_rows = prod_result.all()
    if not products_rows:
        return

    # Create 30 seeded orders over last 30 days
    random.seed(42)
    for i in range(30):
        days_ago = random.randint(0, 29)
        order_date = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=days_ago)
        prod_row = random.choice(products_rows)
        amount = float(prod_row.price) * random.randint(1, 2)

        order_id = str(uuid.uuid4())
        await db.execute(text("""
            INSERT INTO orders (id, user_id, status, amount, currency, notes, created_at, updated_at)
            VALUES (:id, :user_id, 'completed', :amount, 'INR', '{}', :created_at, :created_at)
        """), {"id": order_id, "user_id": customer_id, "amount": amount, "created_at": order_date})

        # Add a payment record
        payment_id = str(uuid.uuid4())
        await db.execute(text("""
            INSERT INTO payments (id, order_id, amount, currency, status, provider, payment_metadata, created_at, updated_at)
            VALUES (:id, :order_id, :amount, 'INR', 'captured', 'demo', '{}', :created_at, :created_at)
        """), {"id": payment_id, "order_id": order_id, "amount": amount, "created_at": order_date})

    # Add 3 failed payments
    for i in range(3):
        days_ago = random.randint(0, 7)
        order_date = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=days_ago)
        prod_row = random.choice(products_rows)
        amount = float(prod_row.price)
        order_id = str(uuid.uuid4())

        await db.execute(text("""
            INSERT INTO orders (id, user_id, status, amount, currency, notes, created_at, updated_at)
            VALUES (:id, :user_id, 'payment_failed', :amount, 'INR', '{}', :created_at, :created_at)
        """), {"id": order_id, "user_id": customer_id, "amount": amount, "created_at": order_date})

    await db.commit()
    print(f"  ✅ Seeded 30 demo orders + 3 failed payments")


if __name__ == "__main__":
    asyncio.run(seed())

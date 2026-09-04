"""
Update all product image_url fields to reliable, always-available Unsplash/Picsum URLs.
Run from backend directory: python update_images.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = "sqlite+aiosqlite:///./paypilot.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Reliable Picsum/Unsplash image URLs per product name
# Using specific Unsplash source URLs by topic that are stable
PRODUCT_IMAGES = {
    # Smartphones
    "Samsung Galaxy S24 Ultra":    "https://images.unsplash.com/photo-1610945264803-c22b62d2a7b3?w=400&h=400&fit=crop&auto=format",
    "iPhone 15 Pro Max":           "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400&h=400&fit=crop&auto=format",
    "OnePlus 12":                  "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop&auto=format",
    "Xiaomi 14 Pro":               "https://images.unsplash.com/photo-1591337676887-a217a6970a8a?w=400&h=400&fit=crop&auto=format",
    "Realme 12 Pro+":              "https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=400&h=400&fit=crop&auto=format",
    # Laptops
    "MacBook Pro 14 M3 Pro":       "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=400&fit=crop&auto=format",
    "ASUS ROG Zephyrus G14":       "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400&h=400&fit=crop&auto=format",
    "Dell XPS 15 (2024)":          "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=400&h=400&fit=crop&auto=format",
    "HP Pavilion 15 (Ryzen 5)":    "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400&h=400&fit=crop&auto=format",
    "Lenovo ThinkPad X1 Carbon":   "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop&auto=format",
    "Acer Nitro V 15 Gaming":      "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=400&h=400&fit=crop&auto=format",
    "HP Spectre x360 14":          "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&h=400&fit=crop&auto=format",
    # Headphones / Earbuds
    "Sony WH-1000XM5":             "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop&auto=format",
    "Bose QuietComfort 45":        "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=400&h=400&fit=crop&auto=format",
    "boAt Rockerz 550":            "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400&h=400&fit=crop&auto=format",
    "Sony WH-1000XM4":             "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&h=400&fit=crop&auto=format",
    "JBL Quantum 360 Gaming":      "https://images.unsplash.com/photo-1524678606370-a47ad25cb82a?w=400&h=400&fit=crop&auto=format",
    "Razer BlackShark V2 Pro":     "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400&h=400&fit=crop&auto=format",
    "HyperX Cloud Alpha Wireless": "https://images.unsplash.com/photo-1586456399729-0c083e01e3ce?w=400&h=400&fit=crop&auto=format",
    "Sony WF-1000XM5":             "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400&h=400&fit=crop&auto=format",
    "boAt Airdopes 141":           "https://images.unsplash.com/photo-1615655406736-b37c4fabf923?w=400&h=400&fit=crop&auto=format",
    # Gaming
    "Razer DeathAdder V3 Pro":            "https://images.unsplash.com/photo-1563297007-0686b7003af7?w=400&h=400&fit=crop&auto=format",
    "Logitech G Pro X Superlight 2":      "https://images.unsplash.com/photo-1612287230202-1ff1d85d1bdf?w=400&h=400&fit=crop&auto=format",
    "Corsair K100 RGB Mechanical":        "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400&h=400&fit=crop&auto=format",
    "ASUS ROG Swift 27\" 360Hz":           "https://images.unsplash.com/photo-1547082299-de196ea013d6?w=400&h=400&fit=crop&auto=format",
    "PlayStation 5 DualSense Controller": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=400&h=400&fit=crop&auto=format",
    # Cameras
    "Sony Alpha A7 IV":  "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400&h=400&fit=crop&auto=format",
    "Canon EOS R50":     "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400&h=400&fit=crop&auto=format",
    "GoPro Hero 12 Black": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=400&h=400&fit=crop&auto=format",
    # Smartwatches
    "Apple Watch Series 9 45mm":     "https://images.unsplash.com/photo-1551816230-ef5deaed4a26?w=400&h=400&fit=crop&auto=format",
    "Samsung Galaxy Watch 6 Classic": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop&auto=format",
    "boAt Wave Sigma 2 Pro":          "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?w=400&h=400&fit=crop&auto=format",
    # Tablets
    "iPad Pro 12.9\" M4":            "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop&auto=format",
    "Samsung Galaxy Tab S9 FE":      "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=400&h=400&fit=crop&auto=format",
    # Laptop Accessories
    "Logitech MX Master 3S":        "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&h=400&fit=crop&auto=format",
    "Logitech MX Keys Mini":        "https://images.unsplash.com/photo-1541140134513-85a161dc4a00?w=400&h=400&fit=crop&auto=format",
    "Dell 27\" 4K USB-C Monitor":    "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400&h=400&fit=crop&auto=format",
    "Targus 15.6\" Laptop Bag":       "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop&auto=format",
    # Phone accessories
    "Anker 65W 3-Port USB-C Charger":      "https://images.unsplash.com/photo-1585338329929-8c5c6e7ecf42?w=400&h=400&fit=crop&auto=format",
    "Spigen Ultra Hybrid iPhone 15 Case":  "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=400&h=400&fit=crop&auto=format",
    # Speakers
    "JBL Charge 5":   "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop&auto=format",
    "Sony SRS-XB33":  "https://images.unsplash.com/photo-1543512214-318c7553f230?w=400&h=400&fit=crop&auto=format",
    # Camera accessories
    "SanDisk 128GB Extreme Pro SD Card": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=400&h=400&fit=crop&auto=format",
    "Joby GorillaPod 3K Kit":            "https://images.unsplash.com/photo-1500828780726-bd8fe31afd7e?w=400&h=400&fit=crop&auto=format",
}

# Fallback images by category
CATEGORY_FALLBACKS = {
    "Smartphones":        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop&auto=format",
    "Laptops":            "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=400&fit=crop&auto=format",
    "Headphones":         "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop&auto=format",
    "Gaming":             "https://images.unsplash.com/photo-1593305841991-05c297ba4575?w=400&h=400&fit=crop&auto=format",
    "Cameras":            "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400&h=400&fit=crop&auto=format",
    "Smartwatches":       "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop&auto=format",
    "Tablets":            "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop&auto=format",
    "Speakers":           "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&h=400&fit=crop&auto=format",
    "Laptop Accessories": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&h=400&fit=crop&auto=format",
    "Phone Cases":        "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=400&h=400&fit=crop&auto=format",
    "Camera Accessories": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400&h=400&fit=crop&auto=format",
}


async def update_images():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT id, name, category FROM products"))
        products = result.all()
        updated = 0
        for row in products:
            pid, name, category = row.id, row.name, row.category
            img = PRODUCT_IMAGES.get(name) or CATEGORY_FALLBACKS.get(category)
            if img:
                await db.execute(
                    text("UPDATE products SET image_url = :url WHERE id = :id"),
                    {"url": img, "id": pid}
                )
                updated += 1
                print(f"  ✓ {name} → {img[:60]}...")
            else:
                print(f"  ⚠ No image for: {name} ({category})")
        await db.commit()
        print(f"\n✅ Updated {updated}/{len(products)} product images")


if __name__ == "__main__":
    asyncio.run(update_images())

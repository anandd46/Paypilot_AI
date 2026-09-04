"""Patch seed.py: add image_url to all products missing them."""
import re

IMAGE_MAP = {
    "Samsung Galaxy S24 Ultra": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=600&q=80",
    "iPhone 15 Pro Max": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600&q=80",
    "OnePlus 12": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=600&q=80",
    "Xiaomi 14 Pro": "https://images.unsplash.com/photo-1567581935884-3349723552ca?w=600&q=80",
    "Realme 12 Pro+": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=600&q=80",
    "MacBook Pro 14 M3 Pro": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&q=80",
    "ASUS ROG Zephyrus G14": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=600&q=80",
    "Dell XPS 15 (2024)": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=600&q=80",
    "HP Pavilion 15 (Ryzen 5)": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&q=80",
    "Lenovo ThinkPad X1 Carbon": "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=600&q=80",
    "Sony WH-1000XM5": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80",
    "Bose QuietComfort 45": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&q=80",
    "boAt Rockerz 550": "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=600&q=80",
    "Sony WH-1000XM4": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=600&q=80",
    "JBL Quantum 360 Gaming": "https://images.unsplash.com/photo-1612444530582-fc66183b16f7?w=600&q=80",
    "Razer DeathAdder V3 Pro": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&q=80",
    "Logitech G Pro X Superlight 2": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&q=80",
    "Corsair K100 RGB Mechanical": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=600&q=80",
    "ASUS ROG Swift 27": "https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=600&q=80",
    "PlayStation 5 DualSense Controller": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=600&q=80",
    "Sony Alpha A7 IV": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&q=80",
    "Canon EOS R50": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=600&q=80",
    "GoPro Hero 12 Black": "https://images.unsplash.com/photo-1499892477393-f675706cbe6e?w=600&q=80",
    "Apple Watch Series 9 45mm": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80",
    "Samsung Galaxy Watch 6 Classic": "https://images.unsplash.com/photo-1617043786394-f977fa12eddf?w=600&q=80",
    "boAt Wave Sigma 2 Pro": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=600&q=80",
    "iPad Pro 12.9": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600&q=80",
    "Samsung Galaxy Tab S9 FE": "https://images.unsplash.com/photo-1589739900243-4b52cd9b104e?w=600&q=80",
    "Logitech MX Master 3S": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&q=80",
    "Logitech MX Keys Mini": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&q=80",
    "Dell 27": "https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=600&q=80",
    "Targus 15.6": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=600&q=80",
    "Anker 65W 3-Port USB-C Charger": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&q=80",
    "Spigen Ultra Hybrid iPhone 15 Case": "https://images.unsplash.com/photo-1601593346740-925612772716?w=600&q=80",
    "JBL Charge 5": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&q=80",
    "Sony SRS-XB33": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&q=80",
    "SanDisk 128GB Extreme Pro SD Card": "https://images.unsplash.com/photo-1618424181497-157f25b6ddd5?w=600&q=80",
    "Joby GorillaPod 3K Kit": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&q=80",
    "Razer BlackShark V2 Pro": "https://images.unsplash.com/photo-1612444530582-fc66183b16f7?w=600&q=80",
    "HyperX Cloud Alpha Wireless": "https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=600&q=80",
    "Sony WF-1000XM5": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&q=80",
    "boAt Airdopes 141": "https://images.unsplash.com/photo-1606220838315-056192d5e927?w=600&q=80",
    "Acer Nitro V 15 Gaming": "https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=600&q=80",
    "HP Spectre x360 14": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&q=80",
}

seed_path = "database/seed/seed.py"
with open(seed_path, "r", encoding="utf-8") as f:
    content = f.read()

added = 0
skipped = 0

for name, url in IMAGE_MAP.items():
    # Find the dict block that contains this product name
    # Pattern: "name": "PRODUCT_NAME" anywhere in a block that DOESN'T already have image_url
    # Strategy: find each product block between curly braces and patch it
    
    # Escape special regex characters in name
    name_escaped = re.escape(name)
    
    # Find the block: look for "name": "...<name>..." followed by closing brace (not too far away)
    # We search for the name, then look backward for the opening { and forward for closing }
    pattern = rf'"name":\s*"{name_escaped}[^"]*"'
    match = re.search(pattern, content)
    if not match:
        print(f"  NOT FOUND: {name}")
        continue
    
    # Find the enclosing product dict: look for the nearest } after the match
    # that's at the right indentation level
    block_start = content.rfind('\n    {', 0, match.start())
    block_end = content.find('\n    },', match.start())
    if block_end == -1:
        block_end = content.find('\n    }', match.start())
    
    if block_start == -1 or block_end == -1:
        print(f"  BLOCK NOT FOUND: {name}")
        continue
    
    block = content[block_start:block_end]
    
    # Check if image_url already exists in this block
    if '"image_url"' in block:
        skipped += 1
        continue
    
    # Insert image_url before the closing brace
    # Find the last line before the closing }
    new_line = f'\n        "image_url": "{url}",'
    # Insert just before the closing of the block
    insert_pos = block_end
    content = content[:insert_pos] + new_line + content[insert_pos:]
    added += 1
    print(f"  + Added image for: {name}")

with open(seed_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"\n✅ Done: {added} images added, {skipped} already had images")

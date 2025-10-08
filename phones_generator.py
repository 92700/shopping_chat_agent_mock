# phones_generator.py
import json, random
from pathlib import Path
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
OUT_FILE = DATA_DIR / "phones.json"

brands = [
    ("Google", "Pixel"), ("Xiaomi", "Redmi"), ("OnePlus", "OnePlus"),
    ("Samsung", "Galaxy"), ("Realme", "Realme"), ("Vivo", "Vivo"),
    ("iQOO", "iQOO"), ("Motorola", "Moto"), ("Oppo", "Oppo"), ("Poco", "Poco")
]
display_sizes = [5.8, 6.0, 6.1, 6.4, 6.5, 6.6, 6.7, 6.78]
processors = [
    "Snapdragon 6 Gen 1", "Snapdragon 7 Gen 1", "Snapdragon 778G", "Snapdragon 8+",
    "Dimensity 7020", "Dimensity 9200", "Apple A15", "Tensor G3"
]
features_pool = ["OIS", "EIS", "Night mode", "IP68", "Wireless charging", "120Hz", "90Hz", "5G", "WiFi 6E"]

phones = []
for i in range(120):
    brand, family = random.choice(brands)
    model_num = random.randint(3, 15) * random.choice([1, 2])
    model = f"{family} {model_num}{random.choice(['', ' Pro', ' Neo', ' Lite'])}".strip()
    price_tier = random.choice([8000, 12000, 18000, 25000, 32000, 45000, 60000])
    price_variation = random.randint(-2000, 5000)
    price_inr = max(6999, price_tier + price_variation)

    main_mp = random.choice([12, 16, 48, 50, 64, 108])
    ultra_mp = random.choice([8, 12, 16, None])
    battery_mah = random.choice([3000, 3500, 4000, 4500, 5000, 5500, 6000])
    charging_w = random.choice([18, 30, 33, 45, 65, 80, 120])
    display = f"{random.choice(display_sizes)} inch AMOLED, {random.choice(['60Hz','90Hz','120Hz'])}"
    has_ois = random.random() < 0.35
    has_eis = random.random() < 0.6
    features = list(set(random.sample(features_pool, k=random.randint(2, 5))))
    if has_ois and "OIS" not in features:
        features.append("OIS")
    if has_eis and "EIS" not in features:
        features.append("EIS")

    phone = {
        "id": f"phone_{i+1}",
        "brand": brand,
        "model": model,
        "price_inr": price_inr,
        "display": display,
        "camera": {"main_mp": main_mp, "ultra_mp": ultra_mp, "features": features},
        "camera_mp": main_mp,
        "battery_mah": battery_mah,
        "charging_w": charging_w,
        "os": random.choice(["Android", "Android (Stock)", "Android (OxygenOS)", "iOS"]),
        "processor": random.choice(processors),
        "weight_g": random.randint(140, 230),
        "dimensions_mm": f"{random.randint(140,170)} x {random.randint(65,80)} x {random.uniform(6.5,9.5):.1f}",
        "one_hand_score": random.randint(4, 10),
        "connectivity": ["5G","WiFi 6", "Bluetooth 5.2"],
        "colors": ["Black","White","Blue"],
        "announced_date": f"{random.randint(2019,2024)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "image": "https://via.placeholder.com/300x200.png?text=Phone+Image",
        "features": features,
        "notes": ""
    }
    phones.append(phone)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(phones, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(phones)} phones to {OUT_FILE}")

# Fixed price data for Blox Fruits
# prices are in (Beli, Robux) format
# If a fruit cannot be bought with Robux (or price unknown), use None

fruit_prices = {
    "rocket": {"beli": 5000, "robux": 50, "formatted_beli": "5,000", "formatted_robux": "50"},
    "spin": {"beli": 7500, "robux": 75, "formatted_beli": "7,500", "formatted_robux": "75"},
    "chop": {"beli": 30000, "robux": 100, "formatted_beli": "30,000", "formatted_robux": "100"},
    "spring": {"beli": 60000, "robux": 180, "formatted_beli": "60,000", "formatted_robux": "180"},
    "bomb": {"beli": 80000, "robux": 220, "formatted_beli": "80,000", "formatted_robux": "220"},
    "smoke": {"beli": 100000, "robux": 250, "formatted_beli": "100,000", "formatted_robux": "250"},
    "spike": {"beli": 180000, "robux": 380, "formatted_beli": "180,000", "formatted_robux": "380"},
    "flame": {"beli": 250000, "robux": 550, "formatted_beli": "250,000", "formatted_robux": "550"},
    "falcon": {"beli": 300000, "robux": 650, "formatted_beli": "300,000", "formatted_robux": "650"},
    "ice": {"beli": 350000, "robux": 750, "formatted_beli": "350,000", "formatted_robux": "750"},
    "sand": {"beli": 420000, "robux": 850, "formatted_beli": "420,000", "formatted_robux": "850"},
    "dark": {"beli": 500000, "robux": 950, "formatted_beli": "500,000", "formatted_robux": "950"},
    "diamond": {"beli": 600000, "robux": 1000, "formatted_beli": "600,000", "formatted_robux": "1,000"},
    "light": {"beli": 650000, "robux": 1100, "formatted_beli": "650,000", "formatted_robux": "1,100"},
    "rubber": {"beli": 750000, "robux": 1200, "formatted_beli": "750,000", "formatted_robux": "1,200"},
    "barrier": {"beli": 800000, "robux": 1250, "formatted_beli": "800,000", "formatted_robux": "1,250"},
    "ghost": {"beli": 1000000, "robux": 1275, "formatted_beli": "1,000,000", "formatted_robux": "1,275"},
    "magma": {"beli": 960000, "robux": 1300, "formatted_beli": "960,000", "formatted_robux": "1,300"},
    "quake": {"beli": 1000000, "robux": 1500, "formatted_beli": "1,000,000", "formatted_robux": "1,500"},
    "buddha": {"beli": 1200000, "robux": 1650, "formatted_beli": "1,200,000", "formatted_robux": "1,650"},
    "love": {"beli": 1300000, "robux": 1700, "formatted_beli": "1,300,000", "formatted_robux": "1,700"},
    "spider": {"beli": 1500000, "robux": 1800, "formatted_beli": "1,500,000", "formatted_robux": "1,800"},
    "sound": {"beli": 1700000, "robux": 1900, "formatted_beli": "1,700,000", "formatted_robux": "1,900"},
    "phoenix": {"beli": 1800000, "robux": 2000, "formatted_beli": "1,800,000", "formatted_robux": "2,000"},
    "portal": {"beli": 1900000, "robux": 2000, "formatted_beli": "1,900,000", "formatted_robux": "2,000"},
    "rumble": {"beli": 2100000, "robux": 2100, "formatted_beli": "2,100,000", "formatted_robux": "2,100"},
    "pain": {"beli": 2300000, "robux": 2200, "formatted_beli": "2,300,000", "formatted_robux": "2,200"},
    "blizzard": {"beli": 2400000, "robux": 2250, "formatted_beli": "2,400,000", "formatted_robux": "2,250"},
    "gravity": {"beli": 2500000, "robux": 2300, "formatted_beli": "2,500,000", "formatted_robux": "2,300"},
    "mammoth": {"beli": 2700000, "robux": 2350, "formatted_beli": "2,700,000", "formatted_robux": "2,350"},
    "t-rex": {"beli": 2700000, "robux": 2350, "formatted_beli": "2,700,000", "formatted_robux": "2,350"},
    "dough": {"beli": 2800000, "robux": 2400, "formatted_beli": "2,800,000", "formatted_robux": "2,400"},
    "shadow": {"beli": 2900000, "robux": 2425, "formatted_beli": "2,900,000", "formatted_robux": "2,425"},
    "venom": {"beli": 3000000, "robux": 2450, "formatted_beli": "3,000,000", "formatted_robux": "2,450"},
    "control": {"beli": 3200000, "robux": 2500, "formatted_beli": "3,200,000", "formatted_robux": "2,500"},
    "spirit": {"beli": 3400000, "robux": 2550, "formatted_beli": "3,400,000", "formatted_robux": "2,550"},
    "dragon": {"beli": 3500000, "robux": 2600, "formatted_beli": "3,500,000", "formatted_robux": "2,600"},
    "leopard": {"beli": 5000000, "robux": 3000, "formatted_beli": "5,000,000", "formatted_robux": "3,000"},
    "kitsune": {"beli": 8000000, "robux": 4000, "formatted_beli": "8,000,000", "formatted_robux": "4,000"},
}

def get_fruit_info(fruit_name):
    # Normalize input
    key = fruit_name.lower().strip()
    return fruit_prices.get(key)

def get_all_fruits():
    return list(fruit_prices.keys())

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Store Economy Engine", layout="wide")

st.title("🏪 Dynamic Store Economy & Priority Engine")
st.caption("Centralized ledger to calculate Universal Buy Scores across all currencies.")

# =========================================================================
# 1. THE INVENTORY LEDGER (Dynamic Data Editor)
# =========================================================================
st.subheader("1. Live Inventory Ledger")
st.markdown("Update your current inventory. The engine will dynamically adjust Demand based on how close you are to your goal.")

# Pre-loaded with data from your spreadsheet screenshots
default_inventory = [
    {"Item": "Satin", "Inventory": 50000, "Goal": 75000, "Base Gem": 2, "Scarcity Index": 0.01},
    {"Item": "Thread", "Inventory": 500, "Goal": 650, "Base Gem": 200, "Scarcity Index": 6.67},
    {"Item": "Forgehammer", "Inventory": 40, "Goal": 500, "Base Gem": 2500, "Scarcity Index": 28.57},
    {"Item": "Hero Widget", "Inventory": 45, "Goal": 50, "Base Gem": 5000, "Scarcity Index": 200.0},
    {"Item": "General Mythic Shard", "Inventory": 450, "Goal": 1000, "Base Gem": 5000, "Scarcity Index": 45.45},
    {"Item": "Truegold", "Inventory": 1200, "Goal": 1500, "Base Gem": 500, "Scarcity Index": 20.0},
    {"Item": "Pet Medallion", "Inventory": 50, "Goal": 60, "Base Gem": 3000, "Scarcity Index": 166.67},
    {"Item": "Taming Mark Advanced", "Inventory": 10, "Goal": 10, "Base Gem": 6000, "Scarcity Index": 250.0},
    {"Item": "Artisan Vision", "Inventory": 100, "Goal": 150, "Base Gem": 1000, "Scarcity Index": 45.45},
    {"Item": "Charm Design", "Inventory": 500, "Goal": 600, "Base Gem": 1000, "Scarcity Index": 15.38},
    {"Item": "Charm Guide", "Inventory": 500, "Goal": 1200, "Base Gem": 1000, "Scarcity Index": 22.22}
]

# Render interactive grid
edited_inv = st.data_editor(
    default_inventory,
    column_config={
        "Item": st.column_config.TextColumn("Item", disabled=True),
        "Inventory": st.column_config.NumberColumn("Current Inventory", min_value=0),
        "Goal": st.column_config.NumberColumn("Target Goal", min_value=1),
        "Base Gem": st.column_config.NumberColumn("Base Gem Value"),
        "Scarcity Index": st.column_config.NumberColumn("Scarcity Index")
    },
    hide_index=True,
    use_container_width=True
)

# =========================================================================
# 2. BACKGROUND MATH ENGINE
# =========================================================================
computed_true_values = {}

for row in edited_inv:
    item = row["Item"].lower()
    
    # 1. Depletion Curve Demand Index (Maxes at 1.0, hits 0.0 when goal met)
    demand_multiplier = max(0.0, (row["Goal"] - row["Inventory"]) / row["Goal"])
    
    # 2. Modified Gem Value = Base Value * Demand Multiplier * Scarcity
    # (We multiply by 10 just to scale the numbers up to match your spreadsheet's higher DI ranges)
    true_value = row["Base Gem"] * (demand_multiplier * 10) * row["Scarcity Index"]
    
    computed_true_values[item] = true_value

# =========================================================================
# 3. SHOP DASHBOARDS
# =========================================================================
st.markdown("---")
st.subheader("2. Priority Shop Dashboards")

hide_completed = st.checkbox("Hide Items with 0 Priority (Goal Met)", value=True)

# Master Shop Dictionaries (Extracted from your screenshots)
shops = {
    "🗡️ Swordland Shop (Swordland Coins)": {
        "satin": 1, "thread": 100, "forgehammer": 1250, 
        "general mythic shard": 2500, "artisan vision": 500, 
        "charm design": 500, "charm guide": 500
    },
    "🛡️ Alliance Champ Shop (Champ Coins)": {
        "satin": 1, "thread": 100, "pet medallion": 1500, 
        "taming mark advanced": 3000
    },
    "🌊 Tidal Shop (Tidal Coins)": {
        "satin": 1, "thread": 100, "forgehammer": 1250, 
        "general mythic shard": 2500, "pet medallion": 1500, 
        "taming mark advanced": 3000, "artisan vision": 500,
        "charm design": 500, "charm guide": 500
    },
    "🔮 Mystery Shop (Mystery Badges)": {
        "hero widget": 500, "forgehammer": 250, "general mythic shard": 500
    }
}

# Layout into two columns
col1, col2 = st.columns(2)
columns = [col1, col2, col1, col2]

for i, (shop_name, shop_inventory) in enumerate(shops.items()):
    with columns[i]:
        st.markdown(f"**{shop_name}**")
        
        shop_results = []
        for item, cost in shop_inventory.items():
            if item in computed_true_values:
                true_val = computed_true_values[item]
                
                # Priority Score = True Value divided by the Currency Cost
                priority_score = true_val / cost
                
                if hide_completed and priority_score <= 0:
                    continue
                    
                shop_results.append({
                    "Item": item.title(),
                    "Cost": cost,
                    "Priority Score": priority_score
                })
        
        if shop_results:
            # Sort highest score to the top
            df_shop = pd.DataFrame(shop_results).sort_values(by="Priority Score", ascending=False)
            
            # Format output for clean reading
            st.dataframe(
                df_shop, 
                column_config={
                    "Priority Score": st.column_config.ProgressColumn(
                        "Priority Score",
                        help="Higher is better.",
                        format="%.1f",
                        min_value=0,
                        max_value=float(df_shop["Priority Score"].max() if not df_shop.empty else 100)
                    )
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.success("All goals met for items in this shop!")
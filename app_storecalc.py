import streamlit as st
import pandas as pd

st.set_page_config(page_title="Store Economy Engine", layout="wide")

st.title("Dynamic Store Economy & Priority Engine")
st.caption("Centralized ledger to calculate Universal Buy Scores across all currencies.")

# =========================================================================
# 1. THE INVENTORY LEDGER (Dynamic Data Editor)
# =========================================================================
st.subheader("1. Live Inventory Ledger")
st.markdown("Update your current inventory. The engine will dynamically adjust Demand and show you the final Modified Gem Value.")

# Preloaded with your core database values from spreadsheet architecture
if "inventory_data" not in st.session_state:
    st.session_state.inventory_data = [
        {"Item": "Satin", "Inventory": 50000, "Goal": 75000, "Base Gem Value": 2, "Scarcity Index": 0.01},
        {"Item": "Thread", "Inventory": 500, "Goal": 650, "Base Gem Value": 200, "Scarcity Index": 6.67},
        {"Item": "Forgehammer", "Inventory": 40, "Goal": 500, "Base Gem Value": 2500, "Scarcity Index": 28.57},
        {"Item": "Hero Widget", "Inventory": 45, "Goal": 50, "Base Gem Value": 5000, "Scarcity Index": 200.0},
        {"Item": "General Mythic Shard", "Inventory": 450, "Goal": 1000, "Base Gem Value": 5000, "Scarcity Index": 45.45},
        {"Item": "Truegold", "Inventory": 1200, "Goal": 1500, "Base Gem Value": 500, "Scarcity Index": 20.0},
        {"Item": "Pet Medallion", "Inventory": 50, "Goal": 60, "Base Gem Value": 3000, "Scarcity Index": 166.67},
        {"Item": "Taming Mark Advanced", "Inventory": 10, "Goal": 10, "Base Gem Value": 6000, "Scarcity Index": 250.0},
        {"Item": "Artisan Vision", "Inventory": 100, "Goal": 150, "Base Gem Value": 1000, "Scarcity Index": 45.45},
        {"Item": "Charm Design", "Inventory": 500, "Goal": 600, "Base Gem Value": 1000, "Scarcity Index": 15.38},
        {"Item": "Charm Guide", "Inventory": 500, "Goal": 1200, "Base Gem Value": 1000, "Scarcity Index": 22.22}
    ]

# Calculate Demand and Modified Gem Values dynamically for visual display in the ledger
display_ledger_data = []
computed_true_values = {}

for row in st.session_state.inventory_data:
    item_lower = row["Item"].lower()
    
    # 1. Depletion Curve Demand Multiplier (0.0 to 1.0)
    demand_multiplier = max(0.0, (row["Goal"] - row["Inventory"]) / row["Goal"])
    
    # 2. Match your spreadsheet's scale (Demand Index range scales by a factor of 10)
    demand_index = demand_multiplier * 10
    
    # 3. Modified Gem Value = Base Gem Value * Demand Index * Scarcity Index
    mod_gem_value = row["Base Gem Value"] * demand_index * row["Scarcity Index"]
    computed_true_values[item_lower] = mod_gem_value
    
    # Append to visual dictionary
    display_ledger_data.append({
        "Item": row["Item"],
        "Inventory": row["Inventory"],
        "Goal": row["Goal"],
        "Base Gem Value": row["Base Gem Value"],
        "Demand Index": demand_index,
        "Modified Gem Value": mod_gem_value
    })

# Render structured data editor with locked column overrides
edited_inv = st.data_editor(
    display_ledger_data,
    column_config={
        "Item": st.column_config.TextColumn("Item", disabled=True),
        "Inventory": st.column_config.NumberColumn("Current Inventory", min_value=0),
        "Goal": st.column_config.NumberColumn("Target Goal", min_value=1),
        "Base Gem Value": st.column_config.NumberColumn("Base Gem Value", disabled=True, format="%d"),
        "Demand Index": st.column_config.NumberColumn("Demand Index (DI)", disabled=True, format="%.2f"),
        "Modified Gem Value": st.column_config.NumberColumn("Modified Gem Value", disabled=True, format="%.1f")
    },
    hide_index=True,
    use_container_width=True
)

# Keep session states synchronized in real-time when inputs are changed inside cells
for idx, row in enumerate(edited_inv):
    st.session_state.inventory_data[idx]["Inventory"] = row["Inventory"]
    st.session_state.inventory_data[idx]["Goal"] = row["Goal"]

# =========================================================================
# 2. SHOP DASHBOARDS
# =========================================================================
st.markdown("---")
st.subheader("2. Priority Shop Dashboards")

hide_completed = st.checkbox("Hide Items with 0 Priority (Goal Met)", value=True)

# Master Shop Matrix Layout Maps
shops = {
    "Swordland Shop (Swordland Coins)": {
        "satin": 1, "thread": 100, "forgehammer": 1250, 
        "general mythic shard": 2500, "artisan vision": 500, 
        "charm design": 500, "charm guide": 500
    },
    "Alliance Champ Shop (Champ Coins)": {
        "satin": 1, "thread": 100, "pet medallion": 1500, 
        "taming mark advanced": 3000
    },
    "Tidal Shop (Tidal Coins)": {
        "satin": 1, "thread": 100, "forgehammer": 1250, 
        "general mythic shard": 2500, "pet medallion": 1500, 
        "taming mark advanced": 3000, "artisan vision": 500,
        "charm design": 500, "charm guide": 500
    },
    "Mystery Shop (Mystery Badges)": {
        "hero widget": 500, "forgehammer": 250, "general mythic shard": 500
    }
}

col1, col2 = st.columns(2)
columns = [col1, col2, col1, col2]

for i, (shop_name, shop_inventory) in enumerate(shops.items()):
    with columns[i]:
        st.markdown(f"**{shop_name}**")
        
        shop_results = []
        for item, cost in shop_inventory.items():
            if item in computed_true_values:
                true_val = computed_true_values[item]
                priority_score = true_val / cost
                
                if hide_completed and priority_score <= 0:
                    continue
                
                shop_results.append({
                    "Item": item.title(),
                    "Cost": cost,
                    "Priority Score": priority_score
                })
        
        if shop_results:
            df_shop = pd.DataFrame(shop_results).sort_values(by="Priority Score", ascending=False)
            st.dataframe(
                df_shop, 
                column_config={
                    "Priority Score": st.column_config.ProgressColumn(
                        "Priority Score",
                        help="Higher score indicates peak transactional value per shop coin spent.",
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
import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Store Economy Engine", layout="wide")

st.title("🏪 Dynamic Store Economy & IVS Engine")
st.caption("Centralized ledger using Intrinsic Value Scores and Logarithmic Scarcity normalization.")

# =========================================================================
# 1. INITIALIZATION & LEDGER
# =========================================================================
if "inventory_data" not in st.session_state:
    st.session_state.inventory_data = [
        {"Item": "Satin", "Inventory": 50000, "Goal": 75000, "Base Gem Value": 2, "Weekly Limit": 102500, "Global Sources": 3},
        {"Item": "Thread", "Inventory": 500, "Goal": 650, "Base Gem Value": 200, "Weekly Limit": 150, "Global Sources": 3},
        {"Item": "Forgehammer", "Inventory": 40, "Goal": 500, "Base Gem Value": 2500, "Weekly Limit": 35, "Global Sources": 4},
        {"Item": "Hero Widget", "Inventory": 45, "Goal": 50, "Base Gem Value": 5000, "Weekly Limit": 5, "Global Sources": 1},
        {"Item": "General Mythic Shard", "Inventory": 450, "Goal": 1000, "Base Gem Value": 5000, "Weekly Limit": 22, "Global Sources": 6},
        {"Item": "Truegold", "Inventory": 1200, "Goal": 1500, "Base Gem Value": 500, "Weekly Limit": 50, "Global Sources": 1},
        {"Item": "Artisan Vision", "Inventory": 100, "Goal": 150, "Base Gem Value": 1000, "Weekly Limit": 22, "Global Sources": 4},
        {"Item": "Charm Design", "Inventory": 500, "Goal": 600, "Base Gem Value": 1000, "Weekly Limit": 65, "Global Sources": 4},
        {"Item": "Charm Guide", "Inventory": 500, "Goal": 1200, "Base Gem Value": 1000, "Weekly Limit": 45, "Global Sources": 4},
        {"Item": "Mithril", "Inventory": 5, "Goal": 20, "Base Gem Value": 10000, "Weekly Limit": 1, "Global Sources": 1}
    ]

# --- NEW: ENGINE VARIATION CONTROLS ---
st.sidebar.markdown("## ⚙️ Mathematical Engine Tuning")
use_demand = st.sidebar.toggle("Apply Demand Index", value=True, help="Toggles scaling based on your current inventory deficits.")
use_scarcity = st.sidebar.toggle("Apply Scarcity Index", value=True, help="Toggles scaling based on item limits and supply lines.")
use_weighting = st.sidebar.toggle("Apply Custom Priority Weights", value=True, help="Toggles secondary value weights (e.g., specific event multipliers).")

hide_completed = st.sidebar.checkbox("Hide Items with 0 Priority", value=True)

# Calculate display ledger & IVS simultaneously
display_ledger_data = []
computed_true_values = {}

for row in st.session_state.inventory_data:
    item_lower = row["Item"].lower()
    
    # Calculate base parts
    demand_factor = max(0.0, (row["Goal"] - row["Inventory"]) / row["Goal"]) * 10
    scarcity_factor = (1.0 / (row["Weekly Limit"] * row["Global Sources"])) * 1000.0
    log_si_factor = math.log10(max(scarcity_factor, 1.1))
    
    # Conditional Switch Check: If turned off, overwrite factor with 1.0 (Neutral Multiplier)
    d_index = demand_factor if use_demand else 1.0
    log_si = log_si_factor if use_scarcity else 1.0
    
    # Compute the true relative value
    mod_gem_value = row["Base Gem Value"] * d_index * log_si
    computed_true_values[item_lower] = mod_gem_value
    
    display_ledger_data.append({
        "Item": row["Item"], "Inventory": row["Inventory"], "Goal": row["Goal"],
        "Base Gem Value": row["Base Gem Value"], "Calculated Scarcity": scarcity_factor,
        "Demand Index": demand_factor, "Modified Gem Value": mod_gem_value
    })

# Render Editor
edited_inv = st.data_editor(display_ledger_data, hide_index=True, use_container_width=True)
for idx, row in enumerate(edited_inv):
    st.session_state.inventory_data[idx]["Inventory"] = row["Inventory"]
    st.session_state.inventory_data[idx]["Goal"] = row["Goal"]

# Add Background Constants (with custom weighting switch hook)
computed_true_values["5 min speedup"] = 0.5
computed_true_values["1hr speedup"] = 60
computed_true_values["100 gems"] = 100.0
computed_true_values["gear chest"] = 500
computed_true_values["g1 widget"] = 3600
computed_true_values["g2 widget"] = 4500
computed_true_values["taming mark advanced"] = 4500.0
computed_true_values["pet medallion"] = 1500

# =========================================================================
# NAVIGATION ARCHITECTURE (TABS)
# =========================================================================
st.markdown("---")
tab_std, tab_event = st.tabs(["🏛️ Permanent Shops", "🎪 Limited-Time Event Shops"])

# =========================================================================
# TAB 1: PERMANENT SHOPS
# =========================================================================
with tab_std:
    st.subheader("Standard Resource Exchanges")
    
    shops = {
        "Swordland Shop (Swordland Coins)": {
            "satin": 1, "thread": 100, "forgehammer": 1250, "general mythic shard": 2500, 
            "artisan vision": 500, "charm design": 500, "charm guide": 500
        },
        "Alliance Champ Shop (Champ Coins)": {
            "satin": 1, "thread": 100, "pet medallion": 1500, "taming mark advanced": 3000
        },
        "Arena Shop (Arena Tokens)": {
            "mythic hero gear": 12500, "forgehammer": 2500, "general mythic shard": 2500,
            "pet medallion": 2400, "taming mark advanced": 4800
        },
        "Kingdom of Power Shop (KVK Coins)": {
            "truegold": 2, "general mythic shard": 25, "artisan vision": 6,
            "charm design": 6, "charm guide": 6
        },
        "Trial Shop (Trial Crystals)": {
            "mithril": 2500, "general mythic shard": 500, "charm design": 250, "charm guide": 250
        },
        "Tidal Shop (Tidal Coins)": {
            "satin": 1, "thread": 100, "forgehammer": 1250, "general mythic shard": 2500, 
            "pet medallion": 1500, "taming mark advanced": 3000, "artisan vision": 500,
            "charm design": 500, "charm guide": 500
        },
        "Mystery Shop (Mystery Badges)": {
            "hero widget": 500, "forgehammer": 250, "general mythic shard": 500
        }
    }
    
    std_col1, std_col2 = st.columns(2)
    std_cols = [std_col1, std_col2, std_col1, std_col2, std_col1, std_col2, std_col1]
    
    for idx, (shop_name, inventory) in enumerate(shops.items()):
        with std_cols[idx]:
            st.markdown(f"**{shop_name}**")
            res = []
            for item, cost in inventory.items():
                if item in computed_true_values:
                    # Check if base gem value or modified score is preferred
                    raw_val = st.session_state.inventory_data[next(i for i, x in enumerate(st.session_state.inventory_data) if x["Item"].lower() == item)]["Base Gem Value"] if (not use_demand and not use_scarcity) else computed_true_values[item]
                    score = raw_val / cost
                    if hide_completed and score <= 0: continue
                    res.append({"Item": item.title(), "Cost": cost, "Priority Score": score})
            
            if res:
                df = pd.DataFrame(res).sort_values(by="Priority Score", ascending=False)
                st.dataframe(df, column_config={"Priority Score": st.column_config.ProgressColumn("Priority Score", format="%.2f", min_value=0, max_value=float(df["Priority Score"].max() if not df.empty else 100))}, hide_index=True, use_container_width=True)
            else:
                st.success("All items optimized or completed.")

# =========================================================================
# TAB 2: LIMITED-TIME EVENT SHOPS
# =========================================================================
with tab_event:
    st.subheader("🎪 Active Special Event Operations")
    
    ev_col1, ev_col2 = st.columns([1, 1])
    
    with ev_col1:
        st.markdown("### 🏆 Elysium Shop Exchange Priority")
        elysium_shop = {
            "forgehammer": 40, "artisan vision": 15, "charm design": 22, 
            "charm guide": 22, "truegold": 15, "gear chest": 42, "general mythic shard": 75
        }
        ely_res = []
        for item, cost in elysium_shop.items():
            if item in computed_true_values:
                score = computed_true_values[item] / cost
                if hide_completed and score <= 0: continue
                ely_res.append({"Item": item.title(), "Elysium Cost": cost, "Priority Score": score})
                
        if ely_res:
            df_ely = pd.DataFrame(ely_res).sort_values(by="Priority Score", ascending=False)
            st.dataframe(df_ely, column_config={"Priority Score": st.column_config.ProgressColumn("Priority Score", format="%.2f", min_value=0, max_value=float(df_ely["Priority Score"].max()))}, hide_index=True, use_container_width=True)
        else:
            st.info("Elysium goals fully finalized.")

    with ev_col2:
        st.markdown("### 🍾 Champagne Bundle Packs Value Mapping")
        
        # Structure: "item_key": (quantity_in_pack, ticket_cost)
        champagne_shop = {
            "mithril": (3, 20000),
            "hero widget": (10, 1000), 
            "g2 widget": (10, 850), 
            "g1 widget": (10, 700), 
            "forgehammer": (10, 500),
            "pet medallion": (5, 1000), 
            "taming mark advanced": (2, 2000), 
            "general mythic shard": (10, 1000),
            "artisan vision": (10, 350), 
            "charm design": (10, 350), 
            "charm guide": (10, 350)
        }
        
        champ_res = []
        for item, (qty, cost) in champagne_shop.items():
            if item in computed_true_values:
                # Isolate matching base asset data row for backup
                inv_row = next((x for x in st.session_state.inventory_data if x["Item"].lower() == item), None)
                base_gem_val = inv_row["Base Gem Value"] if inv_row else computed_true_values.get(item, 0)
                
                # Assign core value depending on switch preferences
                chosen_unit_value = base_gem_val if (not use_demand and not use_scarcity) else computed_true_values[item]
                
                # Apply Weighting Index modifier if toggle is engaged
                if use_weighting:
                    if item == "mithril": 
                        chosen_unit_value *= 1.25 # Injecting a 25% priority weight modifier
                
                total_bundle_value = chosen_unit_value * qty
                priority_score = total_bundle_value / cost if cost > 0 else 0.0
                
                if hide_completed and total_bundle_value <= 0: continue
                champ_res.append({
                    "Pack Asset": item.title(), "Pack Qty": qty, "Ticket Cost": cost,
                    "Total Value": total_bundle_value, "Priority Score": priority_score
                })
                
        if champ_res:
            df_champ = pd.DataFrame(champ_res).sort_values(by="Priority Score", ascending=False)
            st.dataframe(df_champ, column_config={
                "Ticket Cost": st.column_config.NumberColumn("Ticket Cost", format="%d"),
                "Total Value": st.column_config.NumberColumn("Total Value", format="%.0f"),
                "Priority Score": st.column_config.ProgressColumn("Priority Score", format="%.4f", min_value=0, max_value=float(df_champ["Priority Score"].max() if not df_champ.empty else 1.0))
            }, hide_index=True, use_container_width=True)
        else:
            st.info("Champagne value markers hitting zero bounds.")
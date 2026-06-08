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

# Calculate display ledger & IVS simultaneously
display_ledger_data = []
computed_true_values = {}

for row in st.session_state.inventory_data:
    item_lower = row["Item"].lower()
    
    # Logic: Demand (Linear) * Log Scarcity
    demand_index = max(0.0, (row["Goal"] - row["Inventory"]) / row["Goal"]) * 10
    scarcity_index = (1.0 / (row["Weekly Limit"] * row["Global Sources"])) * 1000.0
    log_si = math.log10(max(scarcity_index, 1.1))
    
    mod_gem_value = row["Base Gem Value"] * demand_index * log_si
    computed_true_values[item_lower] = mod_gem_value
    
    display_ledger_data.append({
        "Item": row["Item"], "Inventory": row["Inventory"], "Goal": row["Goal"],
        "Base Gem Value": row["Base Gem Value"], "Calculated Scarcity": scarcity_index,
        "Demand Index": demand_index, "Modified Gem Value": mod_gem_value
    })

# Render Editor
edited_inv = st.data_editor(display_ledger_data, hide_index=True, use_container_width=True)
for idx, row in enumerate(edited_inv):
    st.session_state.inventory_data[idx]["Inventory"] = row["Inventory"]
    st.session_state.inventory_data[idx]["Goal"] = row["Goal"]

# Add Background Constants
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

hide_completed = st.sidebar.checkbox("Hide Items with 0 Priority", value=True)

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
                    score = computed_true_values[item] / cost
                    if hide_completed and score <= 0: continue
                    res.append({"Item": item.title(), "Cost": cost, "Priority Score": score})
            
            if res:
                df = pd.DataFrame(res).sort_values(by="Priority Score", ascending=False)
                st.dataframe(df, column_config={"Priority Score": st.column_config.ProgressColumn("Priority Score", format="%.1f", min_value=0, max_value=float(df["Priority Score"].max() if not df.empty else 100))}, hide_index=True, use_container_width=True)
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
            st.dataframe(df_ely, column_config={"Priority Score": st.column_config.ProgressColumn("Priority Score", format="%.1f", min_value=0, max_value=float(df_ely["Priority Score"].max()))}, hide_index=True, use_container_width=True)
        else:
            st.info("Elysium goals fully finalized.")

    with ev_col2:
        st.markdown("### 🍾 Champagne Bundle Packs Value Mapping")
        champagne_shop = {
            "Mithril": 3, "hero widget": 10, "g2 widget": 10, "g1 widget": 10, "forgehammer": 10,
            "pet medallion": 5, "taming mark advanced": 2, "general mythic shard": 10,
            "artisan vision": 10, "charm design": 10, "charm guide": 10
        }
        champ_res = []
        for item, qty in champagne_shop.items():
            if item in computed_true_values:
                total_bundle_value = computed_true_values[item] * qty
                if hide_completed and total_bundle_value <= 0: continue
                champ_res.append({"Pack Asset": item.title(), "Pack Qty": qty, "Calculated Value": total_bundle_value})
                
        if champ_res:
            df_champ = pd.DataFrame(champ_res).sort_values(by="Calculated Value", ascending=False)
            st.dataframe(df_champ, column_config={"Calculated Value": st.column_config.ProgressColumn("Value Metric Weight", format="%.0f", min_value=0, max_value=float(df_champ["Calculated Value"].max()))}, hide_index=True, use_container_width=True)
        else:
            st.info("Champagne value markers hitting zero bounds.")

    st.markdown("---")
    st.subheader("🌊 Wavebound Voyage Chest Probability Matrix")
    
    v_charms_common  = (computed_true_values.get("charm design", 0) * 3) + (computed_true_values.get("100 gems", 0) * 2) + (computed_true_values.get("5 min speedup", 0) * 12)
    v_charms_premium = (computed_true_values.get("charm design", 0) * 6) + (computed_true_values.get("charm guide", 0) * 3) + (computed_true_values.get("1hr speedup", 0) * 4)
    v_charms_exq     = (computed_true_values.get("charm design", 0) * 9) + (computed_true_values.get("charm guide", 0) * 9) + (computed_true_values.get("general mythic shard", 0) * 2)
    v_charms_mythic  = (computed_true_values.get("charm design", 0) * 30) + (computed_true_values.get("charm guide", 0) * 30) + (computed_true_values.get("general mythic shard", 0) * 6)
    
    v_gear_common  = (computed_true_values.get("thread", 0) * 14) + (computed_true_values.get("satin", 0) * 900) + (computed_true_values.get("5 min speedup", 0) * 12)
    v_gear_premium = (computed_true_values.get("thread", 0) * 35) + (computed_true_values.get("satin", 0) * 3500) + (computed_true_values.get("1hr speedup", 0) * 3)
    v_gear_exq     = (computed_true_values.get("gear chest", 0) * 7) + (computed_true_values.get("artisan vision", 0) * 8) + (computed_true_values.get("general mythic shard", 0) * 2)
    v_gear_mythic  = (computed_true_values.get("gear chest", 0) * 21) + (computed_true_values.get("artisan vision", 0) * 21) + (computed_true_values.get("general mythic shard", 0) * 6)

    merge_premium_target_charms = ((0.75 * v_charms_exq) + (0.25 * v_charms_mythic)) / 3.0
    ev_charms_premium = max(v_charms_premium, merge_premium_target_charms)
    ev_charms_common  = max(v_charms_common, ev_charms_premium / 3.0)
    
    merge_premium_target_gear = ((0.75 * v_gear_exq) + (0.25 * v_gear_mythic)) / 3.0
    ev_gear_premium = max(v_gear_premium, merge_premium_target_gear)
    ev_gear_common  = max(v_gear_common, ev_gear_premium / 3.0)

    chest_matrix_display = [
        {"Event Track": "Wavebound Voyage Charms", "Common Chest EV": ev_charms_common, "Premium Chest EV": ev_charms_premium, "Exquisite Chest Value": v_charms_exq, "Mythic Chest Value": v_charms_mythic, "Merge Action Advice": "MERGE FOR EXQ/MYTHIC" if merge_premium_target_charms > v_charms_premium else "OPEN CHORDS IMMEDIATELY"},
        {"Event Track": "Wavebound Voyage Gov Gear", "Common Chest EV": ev_gear_common, "Premium Chest EV": ev_gear_premium, "Exquisite Chest Value": v_gear_exq, "Mythic Chest Value": v_gear_mythic, "Merge Action Advice": "MERGE FOR EXQ/MYTHIC" if merge_premium_target_gear > v_gear_premium else "OPEN CHORDS IMMEDIATELY"}
    ]
    
    st.table(pd.DataFrame(chest_matrix_display).set_index("Event Track"))
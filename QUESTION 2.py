import json
import operator
import streamlit as st

# ---------------- RULE ENGINE ----------------
OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}

def evaluate_condition(facts, condition):
    field, op, value = condition
    return field in facts and OPS[op](facts[field], value)

def rule_matches(facts, rule):
    return all(evaluate_condition(facts, c) for c in rule["conditions"])

def run_rules(facts, rules):
    matched = [r for r in rules if rule_matches(facts, r)]
    matched = sorted(matched, key=lambda r: r["priority"], reverse=True)
    if not matched:
        return None, []
    return matched[0], matched

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart AC Rule-Based Controller",
    layout="wide"
)

st.title("❄️ Smart Home Air Conditioner Controller")
st.write("Rule-based decision system for smart air conditioner control.")

# ---------------- SIDEBAR INPUT ----------------
with st.sidebar:
    st.header("🏠 Home Conditions")

    temperature = st.number_input("Temperature (°C)", value=22)
    humidity = st.number_input("Humidity (%)", value=46)
    occupancy = st.selectbox("Occupancy", ["OCCUPIED", "EMPTY"])
    time_of_day = st.selectbox(
        "Time of Day",
        ["MORNING", "AFTERNOON", "EVENING", "NIGHT"]
    )
    windows_open = st.checkbox("Windows Open", value=False)

    st.markdown("---")
    rules_json = st.text_area(
        "Rules (JSON)",
        height=350,
        value=json.dumps([
            {
                "name": "Windows open \u2192 turn AC off",
                "priority": 100,
                "conditions": [["windows_open", "==", True]],
                "action": {
                    "ac_mode": "OFF",
                    "fan_speed": "LOW",
                    "setpoint": None,
                    "reason": "Windows are open"
                }
            },
            {
                "name": "No one home \u2192 eco mode",
                "priority": 90,
                "conditions": [
                    ["occupancy", "==", "EMPTY"],
                    ["temperature", ">=", 24]
                ],
                "action": {
                    "ac_mode": "ECO",
                    "fan_speed": "LOW",
                    "setpoint": 27,
                    "reason": "Home empty; save energy"
                }
            },
            {
                "name": "Hot & humid (occupied) \u2192 cool strong",
                "priority": 80,
                "conditions": [
                    ["occupancy", "==", "OCCUPIED"],
                    ["temperature", ">=", 30],
                    ["humidity", ">=", 70]
                ],
                "action": {
                    "ac_mode": "COOL",
                    "fan_speed": "HIGH",
                    "setpoint": 23,
                    "reason": "Hot and humid"
                }
            },
            {
                "name": "Hot (occupied) \u2192 cool",
                "priority": 70,
                "conditions": [
                    ["occupancy", "==", "OCCUPIED"],
                    ["temperature", ">=", 28]
                ],
                "action": {
                    "ac_mode": "COOL",
                    "fan_speed": "MEDIUM",
                    "setpoint": 24,
                    "reason": "Temperature high"
                }
            },
            {
                "name": "Slightly warm (occupied) \u2192 gentle cool",
                "priority": 60,
                "conditions": [
                    ["occupancy", "==", "OCCUPIED"],
                    ["temperature", ">=", 26],
                    ["temperature", "<", 28]
                ],
                "action": {
                    "ac_mode": "COOL",
                    "fan_speed": "LOW",
                    "setpoint": 25,
                    "reason": "Slightly warm"
                }
            },
            {
                "name": "Night (occupied) \u2192 sleep mode",
                "priority": 75,
                "conditions": [
                    ["occupancy", "==", "OCCUPIED"],
                    ["time_of_day", "==", "NIGHT"],
                    ["temperature", ">=", 26]
                ],
                "action": {
                    "ac_mode": "SLEEP",
                    "fan_speed": "LOW",
                    "setpoint": 26,
                    "reason": "Night comfort"
                }
            },
            {
                "name": "Too cold \u2192 turn off",
                "priority": 85,
                "conditions": [["temperature", "<=", 22]],
                "action": {
                    "ac_mode": "OFF",
                    "fan_speed": "LOW",
                    "setpoint": None,
                    "reason": "Already cold"
                }
            }
        ], indent=2)
    )

    run = st.button("Evaluate AC Setting", type="primary")

# ---------------- FACTS ----------------
facts = {
    "temperature": temperature,
    "humidity": humidity,
    "occupancy": occupancy,
    "time_of_day": time_of_day,
    "windows_open": windows_open
}

st.subheader("📌 Current Home Facts")
st.json(facts)

# ---------------- RULE EVALUATION ----------------
if run:
    rules = json.loads(rules_json)
    selected_rule, matched_rules = run_rules(facts, rules)

    if selected_rule:
        action = selected_rule["action"]

        st.subheader("✅ Final AC Decision")
        st.success(f"""
**AC Mode:** {action['ac_mode']}  
**Fan Speed:** {action['fan_speed']}  
**Setpoint:** {action['setpoint']}  
**Reason:** {action['reason']}
""")

        st.subheader("🔍 Matched Rules (by Priority)")
        for r in matched_rules:
            with st.expander(f"{r['name']} (Priority {r['priority']})"):
                st.json(r)
    else:
        st.warning("No rule matched.")

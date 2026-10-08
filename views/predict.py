import streamlit as st

from roadwatch import pipeline as P
from roadwatch.signs import traffic_light
from roadwatch.store import get_bundle
from roadwatch.theme import GREEN, AMBER, RED, callout, html, page_header

bundle = get_bundle()
page_header("Risk check", "Set up a driving situation. The score updates as you change it.")
callout("The model is barely better than guessing (see Model Report), so treat the score as a demonstration, "
        "not as advice about a real trip.")

DEFAULTS = dict(weather="Clear", road_type="Highway", time="Afternoon", traffic="Medium", speed=60, vehicles=3,
                alcohol=False, severity="Low", surface="Dry", vehicle="Car", age=43, exp=39, light="Artificial Light",
                model="Random Forest")
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)

PRESETS = {
    "Clear morning commute": dict(weather="Clear", road_type="City Road", time="Morning", traffic="High", speed=50,
                                  vehicles=4, alcohol=False, surface="Dry", vehicle="Car", age=35, exp=31, light="Daylight"),
    "Rainy night on the highway": dict(weather="Rainy", road_type="Highway", time="Night", traffic="Low", speed=100,
                                       vehicles=2, alcohol=False, surface="Wet", vehicle="Truck", age=45, exp=41,
                                       light="Artificial Light"),
    "Foggy mountain pass": dict(weather="Foggy", road_type="Mountain Road", time="Evening", traffic="Low", speed=50,
                                vehicles=1, alcohol=True, surface="Icy", vehicle="Motorcycle", age=28, exp=24, light="No Light"),
}


def apply_preset(values):
    for k, v in values.items():
        st.session_state[k] = v
    st.session_state["severity"] = "Low"


left, right = st.columns([1.05, 1], gap="large")

with left:
    st.markdown("**Start from a scenario**")
    pcols = st.columns(3)
    for col, (name, vals) in zip(pcols, PRESETS.items()):
        with col:
            st.button(name, key=f"preset_{name}", on_click=apply_preset, args=(vals,))

    st.markdown("#### Road and weather")
    a, b = st.columns(2)
    a.selectbox("Weather", P.options("Weather"), key="weather")
    b.selectbox("Road type", P.options("Road_Type"), key="road_type")
    a.selectbox("Time of day", P.options("Time_of_Day"), key="time")
    b.selectbox("Road surface", P.options("Road_Condition"), key="surface")
    st.selectbox("Lighting", P.options("Road_Light_Condition"), key="light")

    st.markdown("#### Traffic")
    st.select_slider("Traffic density", options=P.options("Traffic_Density"), key="traffic")
    st.slider("Speed limit (km/h)", min_value=20, max_value=220, step=5, key="speed")
    st.caption("Most records are between 30 and 120 km/h. A few show 178 to 213 km/h, which look like data-entry errors.")
    st.slider("Vehicles involved", min_value=1, max_value=14, key="vehicles")

    st.markdown("#### Driver and vehicle")
    st.selectbox("Vehicle", P.options("Vehicle_Type"), key="vehicle")
    st.slider("Driver age", min_value=18, max_value=69, key="age")
    st.slider("Driver experience (years)", min_value=0, max_value=69, key="exp")
    st.caption("In the training data experience follows age very closely (age 43 goes with about 39 years), "
               "so unusual combinations fall outside what the model has seen.")
    st.toggle("Driver has been drinking alcohol", key="alcohol")
    with st.expander("Crash severity (advanced)"):
        st.selectbox("Severity", P.options("Accident_Severity"), key="severity")
        st.caption("This column was part of the training data, so the model expects a value. Leave it at Low if unsure.")

    st.markdown("#### Model")
    st.radio("Which tuned model should answer?", ["Random Forest", "Decision Tree"], key="model", horizontal=True)
    st.caption("Random Forest is the model your notebook saved. Decision Tree is the simpler one.")

ss = st.session_state
TRAFFIC_CODE = {"Low": 0.0, "Medium": 1.0, "High": 2.0}
inputs = {"Weather": ss["weather"], "Road_Type": ss["road_type"], "Time_of_Day": ss["time"],
          "Traffic_Density": TRAFFIC_CODE[ss["traffic"]], "Speed_Limit": float(ss["speed"]),
          "Number_of_Vehicles": float(ss["vehicles"]), "Driver_Alcohol": 1.0 if ss["alcohol"] else 0.0,
          "Accident_Severity": ss["severity"], "Road_Condition": ss["surface"], "Vehicle_Type": ss["vehicle"],
          "Driver_Age": float(ss["age"]), "Driver_Experience": float(ss["exp"]),
          "Road_Light_Condition": ss["light"]}
res = P.predict(bundle, ss["model"], inputs)
p, base = res["proba"], bundle["base_rate"]
if p >= 0.5:
    level, color, title, sub = 2, RED, "Accident predicted", "The model's score is above its 50% alarm line."
elif p >= base:
    level, color, title, sub = 1, AMBER, "Above average risk", (
        f"Higher than the {base * 100:.0f}% average in the data, but below the 50% alarm line.")
else:
    level, color, title, sub = 0, GREEN, "Below average risk", f"Lower than the {base * 100:.0f}% average in the data."

with right:
    st.markdown("#### The model says")
    html(f"""
    <div class="verdict" style="--c:{color}">
      <div>{traffic_light(level, 84)}</div>
      <div>
        <div class="verdict-pct">{p * 100:.0f}%</div>
        <div class="verdict-title">{title}</div>
        <div class="verdict-sub">{sub}</div>
      </div>
    </div>
    <div class="meter" style="--base:{base * 100:.0f}%"><i style="left:{min(p, 1) * 100:.1f}%"></i></div>
    <div class="meter-scale"><span>0%</span><span>average {base * 100:.0f}%</span><span>50%</span><span>100%</span></div>
    """)
    st.markdown("#### What moves this score")
    st.caption("Each row shows how many percentage points a factor adds or removes, compared with a typical value for that factor.")
    if not res["factors"]:
        st.write("Nothing in this scenario moves the score much.")
    rows = ""
    for f, d in res["factors"]:
        cls, arrow = ("up", "&#9650;") if d > 0 else ("down", "&#9660;")
        rows += (f'<div class="factor"><span class="arrow {cls}">{arrow}</span><b>{P.LABEL[f]}</b>'
                 f'<span class="val">{P.display_value(f, inputs[f])}</span>'
                 f'<span class="pts {cls}">{d * 100:+.1f} pts</span></div>')
    html(rows)

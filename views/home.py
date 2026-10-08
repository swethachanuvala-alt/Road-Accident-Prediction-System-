import streamlit as st

from roadwatch.signs import guide_sign, signpost, speed_sign, stop_sign, warning_sign
from roadwatch.store import get_bundle, get_plot_data
from roadwatch.theme import callout, html

df = get_plot_data()
bundle = get_bundle()
m = bundle["metrics"]["Random Forest"]

html(f"""
<div class="hero">
  <div>
    <div class="hero-title">Know the road<br>before you take it.</div>
    <div class="hero-sub">Describe the weather, the road and the driver. A machine learning model trained on
    traffic records estimates how likely an accident is in that situation.</div>
  </div>
  <div class="hero-signs">
    {signpost(warning_sign("!", 92), 64)}
    {signpost(speed_sign(60, 92), 40)}
    {signpost(stop_sign(92), 54)}
  </div>
  <div class="road"></div>
</div>
""")

callout("<b>Learning project.</b> On unseen data this model is about as accurate as always answering "
        "&ldquo;no accident&rdquo;. Use it to explore how a model reacts to road conditions, not to make real safety decisions.")

st.markdown("### Take an exit")
cols = st.columns(3, gap="large")
exits = [("Risk Check", "Exit 1", "views/predict.py", "Check a scenario", "🚦"),
         ("Traffic Data", "Exit 2", "views/explore.py", "Explore the records", "📊"),
         ("Model Report", "Exit 3", "views/performance.py", "See how it performs", "🎯")]
for col, (title, sub, path, label, icon) in zip(cols, exits):
    with col:
        html(guide_sign(title, sub, 300))
        st.page_link(path, label=label, icon=icon)

st.markdown("### The data at a glance")
html(f"""
<div class="signs-row">
  <div class="stat">{speed_sign(len(df), 96)}<div class="stat-cap">traffic records with a known outcome</div></div>
  <div class="stat">{speed_sign(13, 96)}<div class="stat-cap">road, traffic and driver factors per record</div></div>
  <div class="stat">{speed_sign(f"{df['Accident'].mean() * 100:.0f}%", 96)}<div class="stat-cap">of the records ended in an accident</div></div>
  <div class="stat">{speed_sign(f"{m['accuracy'] * 100:.0f}%", 96)}<div class="stat-cap">test accuracy, the same as always saying no</div></div>
</div>
""")

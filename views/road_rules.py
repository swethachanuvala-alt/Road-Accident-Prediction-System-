import streamlit as st

from roadwatch.signs import info_sign, prohibition_sign, speed_sign, stop_sign, warning_sign
from roadwatch.theme import callout, html, page_header

page_header("Rules of the road", "Good habits that matter far more than any model score.")

cards = [
    (speed_sign(60, 84), "Respect the limit",
     "Speed limits assume good conditions. In rain, fog, snow or heavy traffic, drive slower than the limit."),
    (prohibition_sign("DUI", 84), "Never drink and drive",
     "Alcohol slows reactions and judgement. Choose a sober driver, a taxi or public transport."),
    (warning_sign("!", 84), "Respect the weather",
     "Wet, icy and foggy roads need more distance and gentler braking. If you cannot see, slow down or stop somewhere safe."),
    (info_sign("ON", 84), "Be seen",
     "Use headlights at night and in poor visibility, and keep them clean. Dipped beams in fog, never full beam."),
    (stop_sign(84), "Stop means stop",
     "Come to a full stop at stop signs and red lights, and give way where the rules say you must."),
    (info_sign("3s", 84), "Leave a gap",
     "Keep at least a three-second gap to the vehicle ahead, and more on wet or slippery roads."),
    (info_sign("&#9679;", 84), "Wear protection",
     "Seat belts for every passenger, and a properly fastened helmet on every two-wheeler ride."),
    (prohibition_sign("&#9742;", 84), "Eyes on the road",
     "Put the phone away. A message can wait; a crash cannot be undone."),
]
html('<div class="rule-grid">' + "".join(
    f'<div class="rule-card">{svg}<div><div class="rule-title">{t}</div><div class="rule-text">{d}</div></div></div>'
    for svg, t, d in cards) + "</div>")
st.write("")
callout("Local laws differ. Check your own country's traffic rules and the signs on the road in front of you.")

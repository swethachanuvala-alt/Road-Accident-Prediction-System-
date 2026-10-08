import streamlit as st

from roadwatch.store import get_bundle
from roadwatch.theme import callout, html, page_header

bundle = get_bundle()
page_header("About this project", "A small machine learning project, from notebook to web app.")

st.markdown("""
#### The data
840 traffic records with 13 fields: weather, road type, time of day, traffic density, speed limit, number of vehicles,
alcohol, crash severity, road surface, vehicle type, driver age, driver experience and lighting. The target is
whether an accident happened. About 5% of every column is empty; the notebook fills text gaps with the most common
value and number gaps with the median, and so does this app.

#### The models
The notebook trained six model families, tuned each with randomized search, and saved the tuned **Random Forest**.
This app serves that Random Forest and the tuned **Decision Tree**, and you can switch between them on the Risk Check page.

#### The pipeline in this app
1. Fill gaps, then encode the text columns as numbers
2. Split 80% training and 20% testing, keeping the accident share equal in both
3. Standardise the numbers
4. Train the tuned models (no resampling)
5. Score new situations the same way

#### Things worth knowing
- **Accuracy is close to a coin flip.** Always answering &ldquo;no accident&rdquo; is already 71% accurate here, and the models do not beat it.
- **The data looks partly synthetic.** Driver experience tracks age almost exactly, some speed limits are near 200 km/h, and
  factors such as alcohol show no higher accident rate. Real-world road safety research finds the opposite.
- **Crash severity is an outcome.** It only exists after a crash, yet it was used as an input. The app keeps it so the models match the notebook.
- **Units are assumed.** Speed is treated as km/h and traffic density as 0, 1, 2 for low, medium, high.
""")
callout("Ideas to improve it: collect real accident records, remove crash severity from the inputs, "
        "and judge the models on recall for the accident class rather than on accuracy alone.")
html(f'<div class="callout" style="border-left-color:#4DA3FF">Models in this session: {bundle["source"]}.</div>')

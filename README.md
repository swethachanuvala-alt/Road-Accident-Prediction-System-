# Road Watch - Accident Risk Predictor

A multipage Streamlit app for the road accident project (Random Forest and Decision Tree).
Describe a driving situation and the model estimates how likely an accident is.
This is a learning project: the models are only about as accurate as always answering "no accident".

## Run locally (VS Code terminal / cmd)
```
cd road-accident-app
python -m venv venv
venv\Scripts\activate          (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Push this folder to a GitHub repository (`app.py` must be at the repo root).
2. Go to https://share.streamlit.io and click **Create app**.
3. Pick the repository, branch `main`, main file path `app.py`, then **Deploy**.

## Folder layout
```
app.py              entry point + navigation
views/              the six pages
roadwatch/              pipeline (training/prediction), road signs (SVG), theme
data/               dataset_traffic_accident_prediction1.csv
model/              saved models, scaler, encoders (re-create with: python train_model.py)
notebooks/          original notebook
.streamlit/         dark road theme
```
If the saved models were made with a different scikit-learn version, the app silently retrains
from the CSV at start-up (takes about a second), so it keeps working.

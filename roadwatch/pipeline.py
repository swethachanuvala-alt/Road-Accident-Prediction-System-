"""Training + prediction pipeline for the Road Watch app.

Mirrors notebooks/GGST_13.ipynb:
  1. fill missing values (mode for text columns, median for numbers)
  2. label-encode the text columns
  3. 80/20 stratified split (random_state=42)
  4. StandardScaler fitted on the training split (no SMOTE)
  5. the two tuned models from the notebook's RandomizedSearchCV:
     Random Forest (the model the notebook saved) and Decision Tree
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             roc_auc_score)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "dataset_traffic_accident_prediction1.csv"
MODEL_DIR = BASE_DIR / "model"
MODEL_FILES = {"Random Forest": MODEL_DIR / "random_forest_model.pkl",
               "Decision Tree": MODEL_DIR / "Decision_Tree_model.pkl"}
SCALER_FILE = MODEL_DIR / "scaler.pkl"
ENCODER_FILE = MODEL_DIR / "label_encoders.pkl"
META_FILE = MODEL_DIR / "metadata.json"

CATS = ["Weather", "Road_Type", "Time_of_Day", "Accident_Severity",
        "Road_Condition", "Vehicle_Type", "Road_Light_Condition"]
NUMS = ["Traffic_Density", "Speed_Limit", "Number_of_Vehicles", "Driver_Alcohol",
        "Driver_Age", "Driver_Experience"]
TARGET = "Accident"
FEATURES = ["Weather", "Road_Type", "Time_of_Day", "Traffic_Density", "Speed_Limit",
            "Number_of_Vehicles", "Driver_Alcohol", "Accident_Severity", "Road_Condition",
            "Vehicle_Type", "Driver_Age", "Driver_Experience", "Road_Light_Condition"]
LABEL = {"Weather": "Weather", "Road_Type": "Road type", "Time_of_Day": "Time of day",
         "Traffic_Density": "Traffic density", "Speed_Limit": "Speed limit (km/h)",
         "Number_of_Vehicles": "Vehicles involved", "Driver_Alcohol": "Alcohol",
         "Accident_Severity": "Crash severity", "Road_Condition": "Road surface",
         "Vehicle_Type": "Vehicle", "Driver_Age": "Driver age",
         "Driver_Experience": "Driver experience", "Road_Light_Condition": "Lighting"}
# nicer display order for menus and charts
ORDER = {"Weather": ["Clear", "Foggy", "Rainy", "Snowy", "Stormy"],
         "Road_Type": ["City Road", "Highway", "Rural Road", "Mountain Road"],
         "Time_of_Day": ["Morning", "Afternoon", "Evening", "Night"],
         "Road_Condition": ["Dry", "Wet", "Icy", "Under Construction"],
         "Road_Light_Condition": ["Daylight", "Artificial Light", "No Light"],
         "Vehicle_Type": ["Motorcycle", "Car", "Bus", "Truck"],
         "Accident_Severity": ["Low", "Moderate", "High"],
         "Traffic_Density": ["Low", "Medium", "High"],
         "Driver_Alcohol": ["No", "Yes"]}
CODED = {"Traffic_Density": ["Low", "Medium", "High"], "Driver_Alcohol": ["No", "Yes"]}
CLASS_NAMES = ["No accident", "Accident"]

# Best parameters found by the notebook's RandomizedSearchCV
RF_PARAMS = dict(n_estimators=100, min_samples_split=2, min_samples_leaf=2,
                 max_features="sqrt", max_depth=10, random_state=42)
DT_PARAMS = dict(criterion="gini", max_depth=3, min_samples_split=5,
                 min_samples_leaf=10, random_state=42)


# ----------------------------------------------------------------- data
def load_raw() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def load_plot_frame() -> pd.DataFrame:
    """Rows with a known outcome; readable labels; other gaps stay empty."""
    df = load_raw().dropna(subset=[TARGET]).reset_index(drop=True)
    df["Traffic_Density"] = df["Traffic_Density"].map({0.0: "Low", 1.0: "Medium", 2.0: "High"})
    df["Driver_Alcohol"] = df["Driver_Alcohol"].map({0.0: "No", 1.0: "Yes"})
    df["Accident"] = df["Accident"].astype(int)
    df["Outcome"] = df["Accident"].map({0: "No accident", 1: "Accident"})
    return df


def options(col: str) -> list:
    """Menu options for a column, in a friendly order."""
    if col in CODED:
        return CODED[col]
    return ORDER[col]


# ------------------------------------------------------------ modelling
def prepare() -> dict:
    df = load_raw()
    baseline = {}
    for c in CATS:
        baseline[c] = df[c].mode()[0]
        df[c] = df[c].fillna(baseline[c])
    for c in NUMS + [TARGET]:
        med = float(df[c].median())
        if c != TARGET:
            baseline[c] = med
        df[c] = df[c].fillna(med)
    encoders = {}
    for c in CATS:
        encoders[c] = LabelEncoder().fit(df[c])
        df[c] = encoders[c].transform(df[c])
    X = df[FEATURES]
    y = df[TARGET].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    scaler = StandardScaler().fit(X_train)
    return dict(encoders=encoders, baseline=baseline, X_train=X_train, X_test=X_test,
                y_train=y_train, y_test=y_test, scaler=scaler,
                X_train_scaled=scaler.transform(X_train),
                X_test_scaled=scaler.transform(X_test))


def fit_models(data: dict) -> dict:
    A, y = data["X_train_scaled"], data["y_train"]
    return {"Random Forest": RandomForestClassifier(**RF_PARAMS).fit(A, y),
            "Decision Tree": DecisionTreeClassifier(**DT_PARAMS).fit(A, y)}


def evaluate(model, X_test_scaled, y_test) -> dict:
    pred = model.predict(X_test_scaled)
    proba = model.predict_proba(X_test_scaled)[:, 1]
    rep = classification_report(y_test, pred, labels=[0, 1], target_names=CLASS_NAMES,
                                output_dict=True, zero_division=0)
    share = float(np.mean(y_test))
    return dict(accuracy=float(accuracy_score(y_test, pred)),
                roc_auc=float(roc_auc_score(y_test, proba)),
                accident_recall=float(rep["Accident"]["recall"]),
                accident_precision=float(rep["Accident"]["precision"]),
                confusion=confusion_matrix(y_test, pred, labels=[0, 1]).tolist(),
                report=rep, n_test=int(len(y_test)),
                baseline_accuracy=max(share, 1 - share))


def save_artifacts() -> dict:
    data = prepare()
    models = fit_models(data)
    MODEL_DIR.mkdir(exist_ok=True)
    for name, path in MODEL_FILES.items():
        joblib.dump(models[name], path)
    joblib.dump(data["scaler"], SCALER_FILE)
    joblib.dump(data["encoders"], ENCODER_FILE)
    META_FILE.write_text(json.dumps({"sklearn_version": sklearn.__version__}, indent=2))
    return dict(data=data, models=models)


def get_bundle() -> dict:
    """Use the saved models when compatible, otherwise retrain (never fails)."""
    data = prepare()
    models, scaler, source = None, data["scaler"], ""
    try:
        meta = json.loads(META_FILE.read_text())
        if meta.get("sklearn_version") == sklearn.__version__:
            with warnings.catch_warnings():
                warnings.simplefilter("error")
                loaded = {n: joblib.load(p) for n, p in MODEL_FILES.items()}
                s = joblib.load(SCALER_FILE)
            ok = (isinstance(loaded["Random Forest"], RandomForestClassifier)
                  and isinstance(loaded["Decision Tree"], DecisionTreeClassifier)
                  and all(getattr(m, "n_features_in_", 0) == len(FEATURES) for m in loaded.values())
                  and getattr(s, "n_features_in_", 0) == len(FEATURES))
            if ok:
                models, scaler, source = loaded, s, "loaded from the model/ folder"
    except Exception:
        models = None
    if models is None:
        scaler = data["scaler"]
        models = fit_models(data)
        source = "trained at start-up from the CSV"
    metrics = {n: evaluate(m, scaler.transform(data["X_test"]), data["y_test"])
               for n, m in models.items()}
    importances = {n: dict(zip(FEATURES, m.feature_importances_.tolist()))
                   for n, m in models.items()}
    return dict(models=models, scaler=scaler, data=data, metrics=metrics, source=source,
                importances=importances, baseline=data["baseline"],
                base_rate=float(np.mean(data["y_train"])),
                n_train=int(len(data["y_train"])))


# ----------------------------------------------------------- inference
def _encode(bundle: dict, inputs: dict) -> dict:
    enc = bundle["data"]["encoders"]
    return {f: (float(enc[f].transform([inputs[f]])[0]) if f in CATS else float(inputs[f]))
            for f in FEATURES}


def display_value(f: str, v) -> str:
    if f in CODED:
        return CODED[f][int(v)] if not isinstance(v, str) else v
    if f in CATS:
        return str(v)
    if f == "Speed_Limit":
        return f"{float(v):.0f} km/h"
    if f in ("Driver_Age", "Driver_Experience"):
        return f"{float(v):.0f} yrs"
    return f"{float(v):.0f}"


def predict(bundle: dict, model_name: str, inputs: dict) -> dict:
    """Accident probability plus what moves it.

    Each factor's effect = score now minus the score if only that factor were
    set to the typical value used to fill gaps in the data.
    """
    model, scaler, base = bundle["models"][model_name], bundle["scaler"], bundle["baseline"]
    rows = [_encode(bundle, inputs)]
    for f in FEATURES:
        alt = dict(inputs)
        alt[f] = base[f]
        rows.append(_encode(bundle, alt))
    X = pd.DataFrame(rows, columns=FEATURES)
    proba = model.predict_proba(scaler.transform(X))[:, 1]
    p = float(proba[0])
    factors = [(f, p - float(proba[i + 1])) for i, f in enumerate(FEATURES)]
    factors = [x for x in factors if abs(x[1]) >= 0.005]
    factors.sort(key=lambda x: abs(x[1]), reverse=True)
    return dict(proba=p, factors=factors[:6])


def tree_rules(bundle: dict) -> str:
    """The decision tree as plain if/else rules in real units."""
    model, scaler = bundle["models"]["Decision Tree"], bundle["scaler"]
    enc, t = bundle["data"]["encoders"], bundle["models"]["Decision Tree"].tree_
    lines = []

    def names(f):
        return CODED[f] if f in CODED else list(enc[f].classes_)

    def rec(n, depth):
        pad = "|   " * depth
        if t.children_left[n] == t.children_right[n]:
            v = t.value[n][0]
            share = v[1] / v.sum() * 100
            verdict = "Accident" if v[1] > v[0] else "No accident"
            lines.append(f"{pad}=> {verdict}  ({share:.0f}% of {int(t.n_node_samples[n])} training rows had an accident)")
            return
        i = int(t.feature[n])
        f = FEATURES[i]
        thr = t.threshold[n] * scaler.scale_[i] + scaler.mean_[i]
        if f in CATS or f in CODED:
            labels = names(f)
            left = [c for k, c in enumerate(labels) if k <= thr]
            right = [c for k, c in enumerate(labels) if k > thr]
            lines.append(f"{pad}if {LABEL[f]} is {' / '.join(left)}:")
            rec(t.children_left[n], depth + 1)
            lines.append(f"{pad}else:  # {LABEL[f]} is {' / '.join(right)}")
        else:
            lines.append(f"{pad}if {LABEL[f]} <= {thr:.1f}:")
            rec(t.children_left[n], depth + 1)
            lines.append(f"{pad}else:  # {LABEL[f]} > {thr:.1f}")
        rec(t.children_right[n], depth + 1)

    rec(0, 0)
    return "\n".join(lines)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from roadwatch import pipeline as P
from roadwatch.store import get_bundle
from roadwatch.theme import AMBER, callout, page_header, show_chart, style_fig

bundle = get_bundle()
page_header("Model report", "How the models do on 168 records they never saw during training.")

name = st.radio("Model", ["Random Forest", "Decision Tree"], horizontal=True, key="perf_model")
m = bundle["metrics"][name]

c = st.columns(4)
c[0].metric("Accuracy", f"{m['accuracy'] * 100:.1f}%")
c[1].metric("Always say \"no accident\"", f"{m['baseline_accuracy'] * 100:.1f}%")
c[2].metric("Accidents caught", f"{m['accident_recall'] * 100:.0f}%")
c[3].metric("ROC-AUC", f"{m['roc_auc']:.2f}")
callout(f"The {name} scores {m['accuracy'] * 100:.1f}%, while simply answering &ldquo;no accident&rdquo; every time scores "
        f"{m['baseline_accuracy'] * 100:.1f}%. It finds only {m['accident_recall'] * 100:.0f}% of the real accidents, and a ROC-AUC near 0.5 "
        "means its ranking of risky and safe cases is close to random. In this dataset the factors simply do not carry much signal.")

left, right = st.columns(2, gap="large")
with left:
    cm = m["confusion"]
    fig = go.Figure(go.Heatmap(z=cm, x=P.CLASS_NAMES, y=P.CLASS_NAMES, text=cm, texttemplate="%{text}",
                               colorscale=[[0, "#1F232B"], [1, "#FFC400"]], showscale=False))
    fig.update_layout(xaxis_title="Predicted", yaxis_title="Actual", yaxis=dict(autorange="reversed"))
    show_chart(style_fig(fig, 380, "Confusion matrix"))
with right:
    imp = pd.DataFrame({"Factor": [P.LABEL[f] for f in P.FEATURES],
                        "Importance": [bundle["importances"][name][f] for f in P.FEATURES]}).sort_values("Importance")
    bar = px.bar(imp, x="Importance", y="Factor", orientation="h", color_discrete_sequence=[AMBER])
    show_chart(style_fig(bar, 380, "What the model leans on"))

st.markdown("#### The decision tree in plain rules")
st.caption("Categories are shown by name and numbers in their real units.")
st.code(P.tree_rules(bundle), language="text")

st.markdown("#### Every model in the notebook")
comp = pd.DataFrame([
    ["Always say no accident", 0.7143, 0.500, None],
    ["XGBoost (tuned)", 0.7321, 0.542, 0.6876],
    ["Random Forest (tuned)", 0.7202, 0.549, 0.7128],
    ["Logistic Regression (tuned)", 0.7143, 0.543, 0.7158],
    ["SVM (tuned)", 0.7143, 0.526, 0.7128],
    ["KNN (tuned)", 0.7024, 0.542, 0.6473],
    ["Decision Tree (tuned)", 0.6964, 0.552, 0.6235],
], columns=["Model", "Test accuracy", "ROC-AUC", "5-fold CV accuracy (before tuning)"])
st.dataframe(comp, hide_index=True)
cmp_fig = px.bar(comp, x="Model", y="Test accuracy", color_discrete_sequence=[AMBER])
cmp_fig.add_hline(y=0.7143, line_dash="dash", line_color="#FFFFFF", annotation_text="always say no")
cmp_fig.update_yaxes(range=[0.6, 0.76])
show_chart(style_fig(cmp_fig, 360))
callout("Every model lands within a couple of points of the &ldquo;always say no&rdquo; line, so the differences between them are not meaningful. "
        "In your notebook XGBoost has the top tuned test accuracy and the saved model is the Random Forest. "
        "Numbers in this table come from your notebook.")

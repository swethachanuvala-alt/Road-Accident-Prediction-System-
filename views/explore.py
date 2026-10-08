import plotly.express as px
import streamlit as st

from roadwatch import pipeline as P
from roadwatch.store import get_plot_data
from roadwatch.theme import AMBER, OUTCOME_COLORS, page_header, show_chart, style_fig

df = get_plot_data()
page_header("Traffic data", f"{len(df)} records with a known outcome. Some fields are empty in some records, "
                            "so each chart uses the records that have the fields it needs.")

FACTORS = ["Weather", "Road_Type", "Time_of_Day", "Road_Condition", "Road_Light_Condition",
           "Vehicle_Type", "Traffic_Density", "Driver_Alcohol", "Accident_Severity"]
overall = df["Accident"].mean() * 100

tab1, tab2, tab3, tab4 = st.tabs(["Accident rate by factor", "Road and time", "Drivers and speed", "Raw data"])

with tab1:
    f = st.selectbox("Factor", FACTORS, format_func=lambda c: P.LABEL[c], key="factor")
    sub = df.dropna(subset=[f])
    g = sub.groupby(f)["Accident"].agg(["mean", "count"]).reset_index()
    g["order"] = g[f].map({v: i for i, v in enumerate(P.ORDER[f])})
    g = g.sort_values("order")
    g["rate"] = g["mean"] * 100
    g["label"] = g.apply(lambda r: f"{r['rate']:.0f}%  (n={int(r['count'])})", axis=1)
    fig = px.bar(g, x=f, y="rate", text="label", color_discrete_sequence=[AMBER],
                 labels={f: P.LABEL[f], "rate": "Records with an accident (%)"})
    fig.add_hline(y=overall, line_dash="dash", line_color="#FFFFFF",
                  annotation_text=f"overall {overall:.0f}%", annotation_position="top right")
    fig.update_traces(textposition="outside")
    fig.update_yaxes(range=[0, max(60, g["rate"].max() + 12)])
    show_chart(style_fig(fig, 440))
    st.caption("Small groups (a low n) swing a lot by chance. Differences of a few points between bars are usually noise.")

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        rf = st.selectbox("Rows", FACTORS, index=1, format_func=lambda c: P.LABEL[c], key="rows")
    with c2:
        cf = st.selectbox("Columns", FACTORS, index=2, format_func=lambda c: P.LABEL[c], key="cols")
    if rf == cf:
        st.info("Pick two different factors.")
    else:
        sub = df.dropna(subset=[rf, cf])
        pv = sub.pivot_table(index=rf, columns=cf, values="Accident", aggfunc="mean") * 100
        pv = pv.reindex(index=[v for v in P.ORDER[rf] if v in pv.index],
                        columns=[v for v in P.ORDER[cf] if v in pv.columns])
        heat = px.imshow(pv, text_auto=".0f", aspect="auto",
                         color_continuous_scale=["#1F232B", "#FFC400", "#FF4D3D"],
                         labels=dict(x=P.LABEL[cf], y=P.LABEL[rf], color="Accident rate (%)"))
        show_chart(style_fig(heat, 440))
        st.caption("Each cell is the percentage of records with an accident. Cells with only a handful of records are unreliable.")

with tab3:
    c1, c2 = st.columns(2, gap="large")
    with c1:
        h = px.histogram(df.dropna(subset=["Driver_Age"]), x="Driver_Age", color="Outcome", barmode="overlay",
                         opacity=0.75, nbins=26, color_discrete_map=OUTCOME_COLORS,
                         labels={"Driver_Age": "Driver age (years)"})
        show_chart(style_fig(h, 380, "Driver age"))
    with c2:
        s = px.histogram(df.dropna(subset=["Speed_Limit"]), x="Speed_Limit", color="Outcome", barmode="overlay",
                         opacity=0.75, nbins=30, color_discrete_map=OUTCOME_COLORS,
                         labels={"Speed_Limit": "Speed limit (km/h)"})
        show_chart(style_fig(s, 380, "Speed limit"))
    sc = px.scatter(df.dropna(subset=["Driver_Age", "Driver_Experience"]), x="Driver_Age", y="Driver_Experience",
                    color="Outcome", opacity=0.7, color_discrete_map=OUTCOME_COLORS,
                    labels={"Driver_Age": "Driver age (years)", "Driver_Experience": "Driver experience (years)"})
    show_chart(style_fig(sc, 400, "Age against experience"))
    st.caption("Experience almost equals age minus a few years, even for drivers who would have started before they could legally drive. "
               "That, plus speed limits near 200 km/h, suggests the records are partly synthetic or have entry errors.")

with tab4:
    weather = st.multiselect("Weather", P.ORDER["Weather"], default=P.ORDER["Weather"])
    view = df[df["Weather"].isin(weather) | df["Weather"].isna()].drop(columns=["Outcome"])
    st.dataframe(view, hide_index=True)
    st.download_button("Download this table as CSV", view.to_csv(index=False).encode("utf-8"),
                       file_name="traffic_records_selection.csv", mime="text/csv")

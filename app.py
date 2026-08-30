import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Berkeley Admissions: Actual vs. Expected",
    layout="wide"
)

# -----------------------------
# Load and prepare data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard_data.csv", low_memory=False)

    berkeley = df[
        (df["campus"] == "Berkeley") &
        (df["fall_term"].between(2023, 2025)) &
        (df["expected_admit_rate"].notna()) &
        (df["applicants"].notna()) &
        (df["admits"].notna())
    ].copy()

    berkeley["expected_admits"] = (
        berkeley["expected_admit_rate"] *
        berkeley["applicants"]
    )

    return berkeley

berkeley = load_data()

# -----------------------------
# Multi-year school summary
# -----------------------------
summary = berkeley.groupby(
    ["atp_code", "high_school", "city"],
    as_index=False
).agg(
    total_applicants=("applicants", "sum"),
    total_admits=("admits", "sum"),
    expected_admits=("expected_admits", "sum"),
    years=("fall_term", "nunique"),
    positive_years=("admit_rate_residual", lambda x: (x > 0).sum())
)

summary["actual_rate"] = (
    summary["total_admits"] /
    summary["total_applicants"]
)

summary["expected_rate"] = (
    summary["expected_admits"] /
    summary["total_applicants"]
)

summary["outperformance_pp"] = (
    summary["actual_rate"] -
    summary["expected_rate"]
) * 100

# Schools with all 3 years and enough applicants
stable = summary[
    (summary["years"] == 3) &
    (summary["total_applicants"] >= 50)
].copy()

# Consistent outperformers
consistent = stable[
    stable["positive_years"] == 3
].sort_values(
    "outperformance_pp",
    ascending=False
)

# -----------------------------
# Header
# -----------------------------
st.title("Berkeley Admissions: Actual vs. Expected")

st.subheader(
    "Which Bay Area public high schools consistently exceeded"
    "their expected UC Berkeley admit rate from 2023–2025?"
)

st.caption(
    "Expected admit rates account for a-g completion, poverty, "
    "applicant GPA, and school size."
)

# -----------------------------
# Key metrics
# -----------------------------
top_school = consistent.iloc[0]

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Schools Analyzed",
    f"{len(stable):,}"
)

c2.metric(
    "Berkeley Applicants",
    f"{int(stable['total_applicants'].sum()):,}"
)

c3.metric(
    "Top Outperformer",
    top_school["high_school"].title()
)

c4.metric(
    "Top Outperformance",
    f"+{top_school['outperformance_pp']:.1f} pp"
)

st.divider()

# -----------------------------
# Headline finding
# -----------------------------
st.header("Headline Finding")

st.success(
    f"**{top_school['high_school'].title()}** was the strongest consistent "
    f"outperformer. From 2023–2025, its actual Berkeley admit rate was "
    f"**{top_school['actual_rate']:.1%}**, compared with an expected rate of "
    f"**{top_school['expected_rate']:.1%}** — an outperformance of "
    f"**{top_school['outperformance_pp']:.1f} percentage points**."
)

# -----------------------------
# Chart 1: actual vs expected
# -----------------------------
st.header("1. Actual vs. Expected Berkeley Admit Rate")

fig_scatter = px.scatter(
    stable,
    x="expected_rate",
    y="actual_rate",
    size="total_applicants",
    hover_name="high_school",
    hover_data={
        "total_applicants": True,
        "expected_rate": ":.1%",
        "actual_rate": ":.1%",
        "outperformance_pp": ":.1f"
    },
    labels={
        "expected_rate": "Expected Admit Rate",
        "actual_rate": "Actual Admit Rate",
        "total_applicants": "Applicants"
    }
)

max_rate = max(
    stable["actual_rate"].max(),
    stable["expected_rate"].max()
)

fig_scatter.add_trace(
    go.Scatter(
        x=[0, max_rate],
        y=[0, max_rate],
        mode="lines",
        name="Actual = Expected",
        line=dict(dash="dash")
    )
)

fig_scatter.update_layout(
    xaxis_tickformat=".0%",
    yaxis_tickformat=".0%",
    height=550
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.caption(
    "Schools above the dashed line admitted students at a higher rate "
    "than the model predicted. Bubble size represents total Berkeley applicants."
)

# -----------------------------
# Chart 2: top outperformers
# -----------------------------
st.header("2. Most Consistent Outperformers")

top10 = consistent.head(10).sort_values(
    "outperformance_pp",
    ascending=True
)

fig_bar = px.bar(
    top10,
    x="outperformance_pp",
    y="high_school",
    orientation="h",
    text="outperformance_pp",
    labels={
        "outperformance_pp": "Outperformance (percentage points)",
        "high_school": ""
    }
)

fig_bar.update_traces(
    texttemplate="%{text:.1f} pp",
    textposition="outside"
)

fig_bar.update_layout(height=550)

st.plotly_chart(fig_bar, use_container_width=True)

st.caption(
    "To qualify as a consistent outperformer, a school must have data "
    "for all three years, at least 50 total Berkeley applicants, and "
    "an actual admit rate above expectation in every year."
)
# -----------------------------
# Chart 3: year-by-year consistency
# -----------------------------
st.header("3. Year-by-Year Outperformance")

# Get the top 10 consistent outperformers
top_ids = consistent.head(10)["atp_code"].tolist()

heat = berkeley[
    berkeley["atp_code"].isin(top_ids)
].copy()

heat["school_label"] = (
    heat["high_school"].str.title()
    + " — "
    + heat["city"].str.title()
)

# Residual = actual admit rate minus expected admit rate
heat["outperformance_pp"] = (
    heat["admit_rate_residual"] * 100
)

heatmap_data = heat.pivot(
    index="school_label",
    columns="fall_term",
    values="outperformance_pp"
)

# Keep schools ordered by overall outperformance
order = (
    consistent.head(10)
    .assign(
        school_label=lambda x:
            x["high_school"].str.title()
            + " — "
            + x["city"].str.title()
    )["school_label"]
    .tolist()
)

heatmap_data = heatmap_data.reindex(order)

fig_heat = px.imshow(
    heatmap_data,
    text_auto=".1f",
    aspect="auto",
    labels={
        "x": "Fall Term",
        "y": "High School",
        "color": "Difference (pp)"
    }
)

fig_heat.update_layout(
    height=500,
    coloraxis_colorbar_title="pp"
)

st.plotly_chart(fig_heat, use_container_width=True)

st.caption(
    "Each cell shows actual Berkeley admit rate minus expected admit rate "
    "in percentage points. Positive values indicate outperformance."
)
# -----------------------------
# Chart 4: school explorer
# -----------------------------
st.header("4. Explore a School")

stable["school_label"] = (
    stable["high_school"].str.title()
    + " — "
    + stable["city"].str.title()
)

school_label = st.selectbox(
    "Choose a high school",
    sorted(stable["school_label"].tolist())
)

selected = stable[
    stable["school_label"] == school_label
].iloc[0]

school_data = berkeley[
    berkeley["atp_code"] == selected["atp_code"]
].sort_values("fall_term").copy()

school_data["actual_rate"] = (
    school_data["admits"] /
    school_data["applicants"]
)

school_data["difference_pp"] = (
    school_data["actual_rate"] -
    school_data["expected_admit_rate"]
) * 100
school_total_applicants = school_data["applicants"].sum()
school_total_admits = school_data["admits"].sum()

school_actual_rate = (
    school_total_admits /
    school_total_applicants
)

school_expected_rate = (
    (
        school_data["expected_admit_rate"]
        * school_data["applicants"]
    ).sum()
    / school_total_applicants
)

school_difference = (
    school_actual_rate - school_expected_rate
) * 100

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "3-Year Applicants",
    f"{int(school_total_applicants):,}"
)

m2.metric(
    "Actual Admit Rate",
    f"{school_actual_rate:.1%}"
)

m3.metric(
    "Expected Admit Rate",
    f"{school_expected_rate:.1%}"
)

m4.metric(
    "Difference",
    f"{school_difference:+.1f} pp"
)
left, right = st.columns([2, 1])

with left:
    fig_school = go.Figure()

    fig_school.add_trace(
        go.Scatter(
            x=school_data["fall_term"],
            y=school_data["actual_rate"],
            mode="lines+markers",
            name="Actual admit rate"
        )
    )

    fig_school.add_trace(
        go.Scatter(
            x=school_data["fall_term"],
            y=school_data["expected_admit_rate"],
            mode="lines+markers",
            name="Expected admit rate"
        )
    )

    fig_school.update_layout(
        xaxis_title="Fall Term",
        yaxis_title="Admit Rate",
        yaxis_tickformat=".0%",
        height=400
    )

    st.plotly_chart(fig_school, use_container_width=True)

with right:
    display_table = school_data[
        [
            "fall_term",
            "applicants",
            "admits",
            "actual_rate",
            "expected_admit_rate",
            "difference_pp"
        ]
    ].copy()

    display_table.columns = [
        "Year",
        "Applicants",
        "Admits",
        "Actual",
        "Expected",
        "Difference (pp)"
    ]

    display_table["Actual"] = display_table["Actual"].map(
        lambda x: f"{x:.1%}"
    )

    display_table["Expected"] = display_table["Expected"].map(
        lambda x: f"{x:.1%}"
    )

    display_table["Difference (pp)"] = display_table[
        "Difference (pp)"
    ].map(lambda x: f"{x:+.1f}")

    st.dataframe(
        display_table,
        hide_index=True,
        use_container_width=True
    )

# -----------------------------
# Methodology
# -----------------------------
st.divider()

with st.expander("Methodology & Limitations"):
    st.markdown(
        """
### How I measured outperformance

This analysis uses the provided `dashboard_data.csv` and focuses on
Bay Area public high schools with UC Berkeley applicants from
**Fall 2023 through Fall 2025**.

The provided **expected admit rate** accounts for:

- a-g completion
- poverty
- applicant GPA
- school size

I define **outperformance** as the difference between a school's
actual Berkeley admit rate and its expected admit rate.

### What counts as consistent?

A school must:

- have observations in **all three years (2023–2025)**
- have at least **50 total Berkeley applicants**
- exceed its expected admit rate in **each of the three years**

The 50-applicant threshold helps reduce volatility from very small
applicant pools.

### Multi-year calculation

Actual and expected admits are aggregated using applicant counts
before calculating the three-year rates, rather than simply averaging
annual percentages.

### Limitations

These data are aggregated at the high-school level. The results show
school-level patterns and should **not** be interpreted as causal
effects or as predictions of an individual student's admission.
"""
    )

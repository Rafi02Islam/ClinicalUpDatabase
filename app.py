import pandas as pd
import plotly.express as px
import streamlit as st

from src.api import fetch_studies
from src.processing import create_dataframe
from src.geography import (
    expand_trial_countries,
    get_country_counts,
    get_geographic_metrics,
)
from src.ai_explainer import (
    explain_study,
    GeminiQuotaError,
    GeminiExplanationError,
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ClinicalUpDatabase",
    page_icon="🧬",
    layout="wide",
)

BLUE = "#2563EB"
NAVY = "#0F2747"
TEAL = "#0D9488"

COLOR_SEQUENCE = [
    BLUE,
    TEAL,
    "#60A5FA",
    "#7C3AED",
    "#F59E0B",
    "#64748B",
]

PHASE_MAPPING = {
    "EARLY_PHASE1": "Early Phase 1",
    "PHASE1": "Phase 1",
    "PHASE2": "Phase 2",
    "PHASE3": "Phase 3",
    "PHASE4": "Phase 4",
    "NA": "Not Applicable",
}

PHASE_OPTIONS = [
    "Early Phase 1",
    "Phase 1",
    "Phase 2",
    "Phase 3",
    "Phase 4",
    "Not Applicable",
]

# --------------------------------------------------
# VISUAL STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        max-width: 1450px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #0F2747;
    }

    div[data-testid="stMetric"] {
        background-color: #F3F7FC;
        border: 1px solid #DFE8F4;
        border-radius: 12px;
        padding: 16px 20px;
    }

    div[data-testid="stMetricValue"] {
        color: #2563EB;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------


@st.cache_data(ttl=3600)
def load_data(condition, max_pages):
    studies = fetch_studies(
        condition=condition,
        page_size=100,
        max_pages=max_pages,
    )
    return create_dataframe(studies)


def clean_phase(value):
    phases = str(value).split(",")

    return [PHASE_MAPPING.get(phase.strip(), phase.strip()) for phase in phases]


def style_chart(fig, height=350):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=15, r=15, t=45, b=25),
        font=dict(color=NAVY),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🧬 ClinicalUpDatabase")
st.markdown("**Clinical Trial Intelligence Platform**")

st.caption(
    "Explore clinical development activity, recruitment trends, "
    "sponsor landscapes and geographic trial distribution "
    "using publicly available ClinicalTrials.gov data."
)

st.divider()

# --------------------------------------------------
# SEARCH
# --------------------------------------------------

st.subheader("Explore Clinical Trials")

search_col, pages_col = st.columns([3, 1])

with search_col:
    condition = st.text_input(
        "Therapeutic area or medical condition",
        value="breast cancer",
    )

with pages_col:
    max_pages = st.selectbox(
        "Number of studies to retrieve",
        options=[100, 200, 300, 500, 1000],
        index=2,
    )

if "trial_data" not in st.session_state:
    st.session_state.trial_data = None

if "searched_condition" not in st.session_state:
    st.session_state.searched_condition = None

if st.button("🔎 Search Clinical Trials", type="primary"):
    if not condition.strip():
        st.warning("Please enter a therapeutic area.")
    else:
        try:
            with st.spinner("Retrieving clinical trial data..."):
                df_result = load_data(
                    condition.strip(),
                    max_pages // 100,
                )
                st.session_state.trial_data = df_result
                st.session_state.searched_condition = condition.strip()

        except RuntimeError as error:
            st.session_state.trial_data = None
            st.error(str(error))


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if st.session_state.trial_data is None:
    st.info("Enter a therapeutic area and select " "'Search Clinical Trials' to begin.")

else:
    df = st.session_state.trial_data

    if df.empty:
        st.warning("No clinical trials were found.")

    else:
        st.success(
            f"Retrieved {len(df):,} clinical trials "
            f"for {st.session_state.searched_condition}."
        )

        st.caption(
            "Results describe the retrieved sample, not "
            "necessarily all studies matching the search. "
            "Recruitment status and location data may change."
        )

        # ------------------------------------------
        # FILTERS
        # ------------------------------------------

        st.subheader("Filter Studies")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            selected_status = st.multiselect(
                "Recruitment Status",
                options=sorted(df["Status"].dropna().unique()),
            )

        with col2:
            selected_phase = st.multiselect(
                "Trial Phase",
                options=PHASE_OPTIONS,
            )

        with col3:
            selected_type = st.multiselect(
                "Study Type",
                options=sorted(df["Study Type"].dropna().unique()),
            )

        with col4:
            available_countries = sorted(get_country_counts(df)["Country"].tolist())

            selected_countries = st.multiselect(
                "Countries",
                options=available_countries,
                placeholder="All countries",
            )

        filtered_df = df.copy()

        if selected_status:
            filtered_df = filtered_df[filtered_df["Status"].isin(selected_status)]

        if selected_phase:
            filtered_df = filtered_df[
                filtered_df["Phase"].apply(
                    lambda value: any(
                        phase in selected_phase for phase in clean_phase(value)
                    )
                )
            ]

        if selected_type:
            filtered_df = filtered_df[filtered_df["Study Type"].isin(selected_type)]

        if selected_countries:
            expanded = expand_trial_countries(filtered_df)

            matching_ids = expanded.loc[
                expanded["Country"].isin(selected_countries),
                "NCT ID",
            ].unique()

            filtered_df = filtered_df[filtered_df["NCT ID"].isin(matching_ids)]

        st.caption(
            f"Showing {len(filtered_df):,} of " f"{len(df):,} retrieved studies."
        )

        # ------------------------------------------
        # SHARED ANALYTICS
        # ------------------------------------------

        geographic_metrics = get_geographic_metrics(filtered_df)
        country_counts = get_country_counts(filtered_df)

        recruiting_count = int((filtered_df["Status"] == "RECRUITING").sum())

        interventional_count = int(
            (filtered_df["Study Type"] == "INTERVENTIONAL").sum()
        )

        # ------------------------------------------
        # NAVIGATION
        # ------------------------------------------

        overview_tab, geography_tab, explorer_tab, ai_tab = st.tabs(
            [
                "📊 Overview",
                "🌍 Geographic Intelligence",
                "🔬 Trial Explorer",
                "✨ AI Trial Intelligence",
            ]
        )

        # ==========================================
        # OVERVIEW TAB
        # ==========================================

        with overview_tab:
            st.subheader("Clinical Research Overview")

            m1, m2, m3, m4 = st.columns(4)

            with m1:
                st.metric("Studies", f"{len(filtered_df):,}")

            with m2:
                st.metric("Recruiting", f"{recruiting_count:,}")

            with m3:
                st.metric(
                    "Interventional",
                    f"{interventional_count:,}",
                )

            with m4:
                st.metric(
                    "Countries Represented",
                    geographic_metrics["countries_represented"],
                )

            st.divider()

            chart1, chart2 = st.columns(2)

            with chart1:
                st.markdown("#### Study Type Distribution")

                if not filtered_df.empty:
                    fig = px.pie(
                        filtered_df,
                        names="Study Type",
                        hole=0.55,
                        color_discrete_sequence=COLOR_SEQUENCE,
                    )

                    st.plotly_chart(
                        style_chart(fig),
                        width="stretch",
                    )
                else:
                    st.info("No matching studies.")

            with chart2:
                st.markdown("#### Recruitment Status")

                if not filtered_df.empty:
                    status_counts = filtered_df["Status"].value_counts().reset_index()

                    status_counts.columns = [
                        "Status",
                        "Count",
                    ]

                    fig = px.bar(
                        status_counts,
                        x="Status",
                        y="Count",
                        color_discrete_sequence=[BLUE],
                    )

                    fig.update_layout(
                        xaxis_title="",
                        yaxis_title="Number of Studies",
                    )

                    st.plotly_chart(
                        style_chart(fig),
                        width="stretch",
                    )
                else:
                    st.info("No matching studies.")

            st.divider()

            st.subheader("Sponsor Intelligence")

            if not filtered_df.empty:
                sponsor_counts = (
                    filtered_df["Sponsor"].value_counts().head(10).reset_index()
                )

                sponsor_counts.columns = [
                    "Sponsor",
                    "Number of Trials",
                ]

                fig = px.bar(
                    sponsor_counts,
                    x="Number of Trials",
                    y="Sponsor",
                    orientation="h",
                    color_discrete_sequence=[TEAL],
                )

                fig.update_layout(
                    yaxis=dict(categoryorder="total ascending"),
                    xaxis_title="Number of Studies",
                    yaxis_title="",
                )

                st.plotly_chart(
                    style_chart(fig, height=420),
                    width="stretch",
                )

                st.caption(
                    "Sponsors are ranked within the " "currently filtered sample."
                )
            else:
                st.info("No sponsor data for these filters.")

        # ==========================================
        # GEOGRAPHIC INTELLIGENCE TAB
        # ==========================================

        with geography_tab:
            st.subheader("Geographic Trial Intelligence")

            st.write("Explore where clinical studies have " "recorded trial locations.")

            g1, g2, g3 = st.columns(3)

            with g1:
                st.metric(
                    "Countries Represented",
                    geographic_metrics["countries_represented"],
                )

            with g2:
                st.metric(
                    "Studies With Locations",
                    geographic_metrics["trials_with_locations"],
                )

            with g3:
                st.metric(
                    "Multinational Studies",
                    geographic_metrics["multinational_trials"],
                )

            st.divider()

            st.markdown("#### Global Trial Distribution")

            if not country_counts.empty:
                fig = px.choropleth(
                    country_counts,
                    locations="Country",
                    locationmode="country names",
                    color="Number of Trials",
                    hover_name="Country",
                    color_continuous_scale=[
                        "#DBEAFE",
                        "#60A5FA",
                        "#2563EB",
                        "#1E3A8A",
                    ],
                    projection="natural earth",
                )

                fig.update_geos(
                    showcoastlines=True,
                    coastlinecolor="#CBD5E1",
                    showframe=False,
                    showland=True,
                    landcolor="#F3F7FC",
                    showcountries=True,
                    countrycolor="#CBD5E1",
                )

                fig.update_layout(
                    geo=dict(bgcolor="rgba(0,0,0,0)"),
                    coloraxis_colorbar=dict(title="Studies"),
                )

                st.plotly_chart(
                    style_chart(fig, height=500),
                    width="stretch",
                )

                st.caption(
                    "A multinational study is counted once "
                    "per country with a recorded location. "
                    "Country totals therefore must not be "
                    "summed to calculate unique study totals. "
                    "The map reflects the retrieved sample."
                )

                st.divider()

                st.markdown("#### Top 10 Countries")

                top_countries = country_counts.head(10)

                fig = px.bar(
                    top_countries,
                    x="Number of Trials",
                    y="Country",
                    orientation="h",
                    color_discrete_sequence=[BLUE],
                )

                fig.update_layout(
                    yaxis=dict(categoryorder="total ascending"),
                    xaxis_title="Number of Studies",
                    yaxis_title="",
                )

                st.plotly_chart(
                    style_chart(fig, height=420),
                    width="stretch",
                )

                with st.expander("View country-level data"):
                    st.dataframe(
                        country_counts,
                        width="stretch",
                        hide_index=True,
                    )

            else:
                st.info(
                    "No geographic location information "
                    "is available for these studies."
                )

        # ==========================================
        # TRIAL EXPLORER TAB
        # ==========================================

        with explorer_tab:
            st.subheader("Clinical Trial Explorer")

            st.write(
                "Browse individual studies, review "
                "trial information and export results."
            )

            title_search = st.text_input(
                "Search within trial titles or NCT IDs",
                placeholder="Enter a keyword or NCT ID",
            )

            explorer_df = filtered_df.copy()

            if title_search.strip():
                keyword = title_search.strip()

                matching_titles = explorer_df["Title"].str.contains(
                    keyword,
                    case=False,
                    na=False,
                    regex=False,
                )

                matching_ids = explorer_df["NCT ID"].str.contains(
                    keyword,
                    case=False,
                    na=False,
                    regex=False,
                )

                explorer_df = explorer_df[matching_titles | matching_ids]

            st.caption(f"{len(explorer_df):,} studies displayed.")

            st.dataframe(
                explorer_df,
                width="stretch",
                hide_index=True,
                column_config={
                    "Trial Link": st.column_config.LinkColumn(
                        "ClinicalTrials.gov",
                        display_text="View Study",
                    )
                },
            )

            st.divider()

            with st.expander("Data Quality Overview"):
                st.write(
                    "Completeness of selected fields " "within the displayed dataset."
                )

                quality_columns = [
                    "Enrollment",
                    "Start Date",
                    "Countries",
                    "Intervention",
                ]

                quality_records = []

                if not explorer_df.empty:
                    for column in quality_columns:
                        missing = (
                            explorer_df[column].isna()
                            | explorer_df[column].eq("Not available")
                        ).sum()

                        completeness = (1 - missing / len(explorer_df)) * 100

                        quality_records.append(
                            {
                                "Field": column,
                                "Missing Records": int(missing),
                                "Completeness (%)": round(completeness, 1),
                            }
                        )

                    st.dataframe(
                        pd.DataFrame(quality_records),
                        width="stretch",
                        hide_index=True,
                    )
                else:
                    st.info("No studies to analyse.")

            csv = explorer_df.to_csv(index=False)

            st.download_button(
                "📥 Download Filtered Dataset (CSV)",
                data=csv,
                file_name="ClinicalUpDatabase_trials.csv",
                mime="text/csv",
            )

        # ==========================================
        # AI TRIAL INTELLIGENCE TAB
        # ==========================================

        with ai_tab:
            st.subheader("AI Trial Explainer")

            st.write(
                "Choose a clinical trial and generate a "
                "plain-English explanation based on its "
                "official ClinicalTrials.gov record."
            )

            st.caption(
                "AI explanations are generated only when requested. "
                "Responses are cached to reduce free-tier usage."
            )

            if filtered_df.empty:
                st.info("No studies match the current filters.")

            else:
                study_choices = (
                    filtered_df[["NCT ID", "Title"]]
                    .dropna(subset=["NCT ID"])
                    .drop_duplicates(subset=["NCT ID"])
                )

                study_ids = study_choices["NCT ID"].tolist()

                study_titles = dict(
                    zip(
                        study_choices["NCT ID"],
                        study_choices["Title"],
                    )
                )

                chosen_nct = st.selectbox(
                    "Select a clinical trial",
                    options=study_ids,
                    format_func=lambda nct: (
                        f"{nct} — " f"{str(study_titles.get(nct, ''))[:105]}"
                    ),
                )

                st.link_button(
                    "View official study record",
                    f"https://clinicaltrials.gov/study/{chosen_nct}",
                )

                if st.button(
                    "✨ Generate AI Explanation",
                    type="primary",
                ):
                    try:
                        with st.spinner("Retrieving and explaining the study..."):
                            explanation = explain_study(chosen_nct)

                        st.session_state["ai_last_explanation"] = (
                            chosen_nct,
                            explanation,
                        )

                    except GeminiQuotaError:
                        st.warning(
                            "The free Gemini API quota is currently "
                            "unavailable. Please try again later. "
                            "No paid API fallback is used."
                        )

                    except GeminiExplanationError as error:
                        st.error(str(error))

                previous = st.session_state.get("ai_last_explanation")

                if previous and previous[0] == chosen_nct:
                    st.divider()
                    st.markdown(previous[1])

                    st.caption(
                        "AI-generated explanation. May contain "
                        "errors or omissions. Verify against "
                        "the official record. Not medical advice."
                    )

        # ------------------------------------------
        # FOOTER
        # ------------------------------------------

        st.divider()

        st.caption(
            "ClinicalUpDatabase uses publicly available "
            "ClinicalTrials.gov information. "
            "Verify study details against the original "
            "registry records. This tool does not provide "
            "medical advice."
        )

import streamlit as st
import plotly.express as px

from src.api import fetch_studies
from src.processing import create_dataframe

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(page_title="ClinicalUpDatabase", page_icon="🧬", layout="wide")

st.title("🧬 ClinicalUpDatabase")
st.subheader("Clinical Trial Intelligence Dashboard")

st.write(
    "Explore clinical trials, development phases, "
    "recruitment activity and sponsor landscapes "
    "using ClinicalTrials.gov data."
)


# --------------------------------------------------
# DATA RETRIEVAL
# --------------------------------------------------


@st.cache_data(ttl=3600)
def load_data(condition, max_pages):
    studies = fetch_studies(condition=condition, page_size=100, max_pages=max_pages)

    return create_dataframe(studies)


if "trial_data" not in st.session_state:
    st.session_state.trial_data = None


# --------------------------------------------------
# SEARCH
# --------------------------------------------------

condition = st.text_input("Search therapeutic area", value="breast cancer")

max_pages = st.slider("Number of pages to retrieve", min_value=1, max_value=10, value=3)

if st.button("Search Clinical Trials"):

    if not condition.strip():
        st.warning("Please enter a therapeutic area.")

    else:
        try:
            with st.spinner("Retrieving clinical trial data..."):
                st.session_state.trial_data = load_data(condition.strip(), max_pages)

        except RuntimeError as error:
            st.session_state.trial_data = None
            st.error(str(error))


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if st.session_state.trial_data is not None:

    df = st.session_state.trial_data

    if df.empty:
        st.warning("No studies found.")

    else:
        st.success(f"Retrieved {len(df)} clinical trials.")

        st.caption(
            "Results represent the retrieved sample, "
            "not necessarily all matching clinical trials."
        )

        # ------------------------------------------
        # INTERACTIVE FILTERS
        # ------------------------------------------

        st.subheader("Filter Clinical Trials")

        col1, col2, col3 = st.columns(3)

        with col1:
            selected_status = st.multiselect(
                "Recruitment Status", options=sorted(df["Status"].dropna().unique())
            )

        with col2:
            phase_options = [
                "Early Phase 1",
                "Phase 1",
                "Phase 2",
                "Phase 3",
                "Phase 4",
                "Not Applicable",
            ]

            selected_phase = st.multiselect("Trial Phase", options=phase_options)

        with col3:
            selected_type = st.multiselect(
                "Study Type", options=sorted(df["Study Type"].dropna().unique())
            )

        # ------------------------------------------
        # APPLY FILTERS
        # ------------------------------------------

        filtered_df = df.copy()

        # Recruitment status filter
        if selected_status:
            filtered_df = filtered_df[filtered_df["Status"].isin(selected_status)]

        # Trial phase filter
        if selected_phase:

            phase_mapping = {
                "EARLY_PHASE1": "Early Phase 1",
                "PHASE1": "Phase 1",
                "PHASE2": "Phase 2",
                "PHASE3": "Phase 3",
                "PHASE4": "Phase 4",
                "NA": "Not Applicable",
            }

            def matches_phase(value):
                phases = str(value).split(",")

                cleaned_phases = [
                    phase_mapping.get(phase.strip(), phase.strip()) for phase in phases
                ]

                return any(phase in selected_phase for phase in cleaned_phases)

            filtered_df = filtered_df[filtered_df["Phase"].apply(matches_phase)]

        # Study type filter
        if selected_type:
            filtered_df = filtered_df[filtered_df["Study Type"].isin(selected_type)]

        st.write(
            f"Showing **{len(filtered_df)}** " f"of **{len(df)}** retrieved studies."
        )

        # ------------------------------------------
        # SUMMARY METRICS
        # ------------------------------------------

        st.divider()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Studies", len(filtered_df))

        with col2:
            interventional = (filtered_df["Study Type"] == "INTERVENTIONAL").sum()

            st.metric("Interventional Studies", int(interventional))

        with col3:
            recruiting = (filtered_df["Status"] == "RECRUITING").sum()

            st.metric("Recruiting Studies", int(recruiting))

        # ------------------------------------------
        # STUDY TYPE AND RECRUITMENT CHARTS
        # ------------------------------------------

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Study Type Distribution")

            if not filtered_df.empty:
                fig = px.pie(
                    filtered_df,
                    names="Study Type",
                    title="Interventional vs Observational",
                    hole=0.4,
                )

                st.plotly_chart(fig, width="stretch")
            else:
                st.info("No studies match these filters.")

        with col2:
            st.subheader("Recruitment Status")

            if not filtered_df.empty:
                status_counts = filtered_df["Status"].value_counts().reset_index()

                status_counts.columns = ["Status", "Count"]

                fig = px.bar(
                    status_counts,
                    x="Status",
                    y="Count",
                    title="Clinical Trial Recruitment Status",
                )

                st.plotly_chart(fig, width="stretch")
            else:
                st.info("No studies match these filters.")

        # ------------------------------------------
        # SPONSOR INTELLIGENCE
        # ------------------------------------------

        st.divider()

        st.subheader("Sponsor Intelligence")

        st.write(
            "Explore the organisations sponsoring "
            "clinical trials in the selected dataset."
        )

        if not filtered_df.empty:

            sponsor_counts = (
                filtered_df["Sponsor"].value_counts().head(10).reset_index()
            )

            sponsor_counts.columns = ["Sponsor", "Number of Trials"]

            fig = px.bar(
                sponsor_counts,
                x="Number of Trials",
                y="Sponsor",
                orientation="h",
                title="Top 10 Trial Sponsors",
            )

            fig.update_layout(yaxis={"categoryorder": "total ascending"})

            st.plotly_chart(fig, width="stretch")

        else:
            st.info("No sponsor data available " "for the selected filters.")

        # ------------------------------------------
        # CLINICAL TRIAL DATASET
        # ------------------------------------------

        st.divider()

        st.subheader("Clinical Trial Dataset")

        st.dataframe(
            filtered_df,
            width="stretch",
            hide_index=True,
            column_config={
                "Trial Link": st.column_config.LinkColumn(
                    "ClinicalTrials.gov", display_text="View Study"
                )
            },
        )

        # ------------------------------------------
        # DATA QUALITY
        # ------------------------------------------

        st.divider()

        with st.expander("Data Quality Overview"):

            st.write(
                "Review missing information within " "the currently filtered dataset."
            )

            if not filtered_df.empty:

                quality_columns = [
                    "Enrollment",
                    "Start Date",
                    "Countries",
                    "Intervention",
                ]

                quality_records = []

                for column in quality_columns:

                    missing = (
                        filtered_df[column].isna()
                        | filtered_df[column].eq("Not available")
                    ).sum()

                    completeness = (1 - missing / len(filtered_df)) * 100

                    quality_records.append(
                        {
                            "Field": column,
                            "Missing Records": int(missing),
                            "Completeness (%)": round(completeness, 1),
                        }
                    )

                st.dataframe(quality_records, width="stretch", hide_index=True)

            else:
                st.info("No studies available for quality analysis.")

        # ------------------------------------------
        # DOWNLOAD DATA
        # ------------------------------------------

        csv = filtered_df.to_csv(index=False)

        st.download_button(
            label="📥 Download Filtered Dataset (CSV)",
            data=csv,
            file_name="ClinicalUpDatabase_trials.csv",
            mime="text/csv",
        )


# 🧬 ClinicalUpDatabase

### Clinical Trial Intelligence Dashboard

ClinicalUpDatabase is an interactive clinical trial intelligence platform built with Python and powered by the ClinicalTrials.gov API.

It enables users to explore clinical research activity, investigate therapeutic areas, analyse trial development phases and identify organisations sponsoring clinical studies.

The project demonstrates the application of clinical research knowledge, data processing and interactive visualisation to publicly available clinical trial information.

## Features

- **Therapeutic Area Search:** Retrieve clinical studies by medical condition.
- **Trial Phase Analysis:** Filter studies by development phase, including combined-phase trials.
- **Recruitment Intelligence:** Explore recruitment status and identify actively recruiting studies.
- **Sponsor Intelligence:** Identify leading clinical trial sponsors within a selected dataset.
- **Study Classification:** Compare interventional and observational research.
- **Data Quality Analysis:** Evaluate completeness of selected clinical trial fields.
- **Interactive Visualisations:** Explore clinical research trends using Plotly charts.
- **CSV Export:** Download filtered clinical trial datasets.
- **Direct Trial Access:** Open individual study records on ClinicalTrials.gov.

## Technology Stack

- Python
- pandas
- Streamlit
- Plotly
- Requests
- ClinicalTrials.gov API v2

## Data Source

ClinicalUpDatabase retrieves publicly available clinical trial information through the ClinicalTrials.gov API.

Results represent a retrieved sample and may not include every study matching a search.

Study information is provided for research and analytical purposes and should be verified against the original ClinicalTrials.gov records.

## Running Locally

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/ClinicalUpDatabase.git
cd ClinicalUpDatabase
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Launch the dashboard:

```bash
python -m streamlit run app.py
```

## Future Development

Planned enhancements include:

- Geographic analysis of clinical trial activity
- Advanced trial comparison tools
- Clinical development pipeline analysis
- Improved sponsor and therapeutic-area intelligence
- AI-assisted explanations of clinical trial information

## Project Status

Active development. The initial interactive dashboard is functional, with additional features planned.

## Author

Developed as an independent clinical research and data analytics portfolio project.

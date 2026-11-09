
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

## AI-Assisted Development

ClinicalUpDatabase was developed using a combination of clinical research knowledge, Python programming, data analytics and AI-assisted development workflows.

Generative AI tools were leveraged to support:

- **Software Development:** Accelerating the implementation of Python functions, API integration and interactive dashboard components.
- **Debugging and Troubleshooting:** Identifying and resolving issues involving data processing, application logic and filtering.
- **Code Optimisation:** Improving code structure, readability and maintainability through iterative refinement.
- **Problem-Solving:** Exploring technical approaches, testing implementations and translating project requirements into working functionality.

AI-assisted suggestions were incorporated into an iterative development process involving local testing, debugging and validation.

The project demonstrates how generative AI can be combined with domain-specific scientific knowledge to accelerate the development of practical research tools.

## Planned AI Integration

Future development will explore integrating large language models (LLMs) directly into ClinicalUpDatabase.

Potential features include:

- **Plain-Language Trial Summaries:** Translating complex clinical trial descriptions into accessible explanations.
- **AI-Assisted Trial Comparison:** Highlighting differences between clinical study designs, interventions and eligibility criteria.
- **Clinical Research Insights:** Supporting exploration of trial characteristics and emerging research activity.

These capabilities are planned and are not currently available in the dashboard. AI-generated content would require appropriate validation and clear links to its underlying clinical trial sources.

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

## Geographic Trial Intelligence

ClinicalUpDatabase includes interactive geographic analysis of clinical trial activity.

Features include:

- Interactive global map visualising trial locations by country.
- Country-level filtering across the dashboard.
- Rankings of countries represented in the retrieved dataset.
- Identification of multinational clinical studies.
- Geographic metrics calculated using unique clinical trial identifiers to avoid double-counting studies within individual countries.

Geographic analyses reflect recorded study locations within the retrieved ClinicalTrials.gov sample, rather than the complete global clinical trial landscape.

## Live Application

Explore ClinicalUpDatabase: https://clinicalupdatabase.streamlit.app/
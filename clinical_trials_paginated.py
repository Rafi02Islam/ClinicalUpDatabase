import requests
import pandas as pd


url = "https://clinicaltrials.gov/api/v2/studies"

params = {
    "query.cond": "breast cancer",
    "pageSize": 100
}

all_studies = []

max_pages = 3
page_count = 0
next_page_token = None


while page_count < max_pages:

    if next_page_token:
        params["pageToken"] = next_page_token

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Request failed with status code: {response.status_code}")
        break

    data = response.json()

    studies = data["studies"]

    all_studies.extend(studies)

    page_count += 1

    print(
        f"Page {page_count} retrieved — "
        f"{len(studies)} studies found."
    )

    next_page_token = data.get("nextPageToken")

    if not next_page_token:
        print("No more pages available.")
        break


print(f"\nTotal studies retrieved: {len(all_studies)}")
trial_records = []

for study in all_studies:
    protocol = study["protocolSection"]

    identification = protocol["identificationModule"]
    status = protocol["statusModule"]
    sponsor_module = protocol["sponsorCollaboratorsModule"]
    design = protocol["designModule"]
    arms = protocol.get("armsInterventionsModule", {})

    nct_id = identification["nctId"]
    title = identification["briefTitle"]

    overall_status = status["overallStatus"]

    sponsor = sponsor_module["leadSponsor"]["name"]

    phases = design.get("phases", ["Not Applicable"])
    phase = ", ".join(phases)

    enrollment_info = design.get("enrollmentInfo", {})
    enrollment = enrollment_info.get("count")

    study_type = design.get("studyType", "Not available")

    start_date_info = status.get("startDateStruct", {})
    start_date = start_date_info.get("date", "Not available")

    contacts_locations = protocol.get("contactsLocationsModule", {})
    locations = contacts_locations.get("locations", [])

    countries = sorted({
    location.get("country")
    for location in locations
    if location.get("country")
})

    country_text = (
    ", ".join(countries)
    if countries
    else "Not available"
)

    interventions = arms.get("interventions", [])

    intervention_types = [
        intervention.get("type", "Unknown")
        for intervention in interventions
    ]

    intervention_type_text = (
        ", ".join(sorted(set(intervention_types)))
        if intervention_types
        else "Not available"
    )

    intervention_names = [
        intervention.get("name", "Unknown")
        for intervention in interventions
    ]

    intervention_text = (
        ", ".join(intervention_names)
        if intervention_names
        else "Not available"
    )

    trial_record = {
        "NCT ID": nct_id,
        "Title": title,
        "Study Type": study_type,
        "Phase": phase,
        "Status": overall_status,
        "Sponsor": sponsor,
        "Enrollment": enrollment,
        "Intervention Type": intervention_type_text,
        "Intervention": intervention_text,
        "Start Date": start_date,
        "Countries": country_text,
    }

    trial_records.append(trial_record)

df = pd.DataFrame(trial_records)

print("\nClinicalUp Dataset:")
print(df)

print(f"\nDataset shape: {df.shape}")
print("\nStudy type breakdown:")
print(df["Study Type"].value_counts())
print("\nIntervention type breakdown:")
print(df["Intervention Type"].value_counts().head(15))
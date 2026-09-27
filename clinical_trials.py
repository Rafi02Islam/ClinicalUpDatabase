import requests
import pandas as pd


url = "https://clinicaltrials.gov/api/v2/studies"

params = {
    "query.cond": "breast cancer",
    "pageSize": 10
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()

    studies = data["studies"]

    print(f"ClinicalUpDatabase found {len(studies)} studies.\n")

    trial_records = []

    for study in studies:
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
        enrollment = enrollment_info.get("count", "Not available")

        interventions = arms.get("interventions", [])

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
            "Phase": phase,
            "Status": overall_status,
            "Sponsor": sponsor,
            "Enrollment": enrollment,
            "Intervention": intervention_text
        }

        trial_records.append(trial_record)

    df = pd.DataFrame(trial_records)

    print("\nClinicalUpDatabase Dataset:")
    print(df)
    print("\n--- ClinicalUp Analysis ---")

    print(f"\nTotal trials: {len(df)}")

    print("\nTrial phase breakdown:")
    print(df["Phase"].value_counts())

    print("\nRecruitment status breakdown:")
    print(df["Status"].value_counts())

    print("\nTop sponsors:")
    print(df["Sponsor"].value_counts().head(5))

    print("\nEnrollment statistics:")
    print(df["Enrollment"].describe())
else:
    print(f"Request failed with status code: {response.status_code}")
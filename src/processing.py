
import pandas as pd


def create_dataframe(studies):
    trial_records = []

    for study in studies:
        protocol = study["protocolSection"]

        identification = protocol["identificationModule"]
        status = protocol["statusModule"]
        sponsor_module = protocol["sponsorCollaboratorsModule"]
        design = protocol["designModule"]
        arms = protocol.get("armsInterventionsModule", {})

        # Study identification
        nct_id = identification["nctId"]
        trial_url = f"https://clinicaltrials.gov/study/{nct_id}"
        title = identification["briefTitle"]

        # Recruitment status and sponsor
        overall_status = status["overallStatus"]
        sponsor = sponsor_module["leadSponsor"]["name"]

        # Trial phase normalisation
        phases = design.get("phases") or []

        phase_labels = {
            "EARLY_PHASE1": "Early Phase 1",
            "PHASE1": "Phase 1",
            "PHASE2": "Phase 2",
            "PHASE3": "Phase 3",
            "PHASE4": "Phase 4",
            "NA": "Not Applicable"
        }

        cleaned_phases = [
            phase_labels.get(p, p)
            for p in phases
        ]

        phase = (
            ", ".join(cleaned_phases)
            if cleaned_phases
            else "Not Applicable"
        )

        # Study design and enrollment
        enrollment_info = design.get("enrollmentInfo", {})
        enrollment = enrollment_info.get("count")
        study_type = design.get(
            "studyType",
            "Not available"
        )

        # Start date
        start_date_info = status.get("startDateStruct", {})
        start_date = start_date_info.get(
            "date",
            "Not available"
        )

        # Study locations
        contacts_locations = protocol.get(
            "contactsLocationsModule", {}
        )
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

        # Interventions
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

        # Build one structured record per study
        trial_record = {
            "NCT ID": nct_id,
            "Trial Link": trial_url,
            "Title": title,
            "Study Type": study_type,
            "Phase": phase,
            "Status": overall_status,
            "Sponsor": sponsor,
            "Enrollment": enrollment,
            "Start Date": start_date,
            "Countries": country_text,
            "Intervention Type": intervention_type_text,
            "Intervention": intervention_text
        }

        trial_records.append(trial_record)

    df = pd.DataFrame(trial_records)

    return df

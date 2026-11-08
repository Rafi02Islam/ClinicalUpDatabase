import requests

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


def fetch_studies(condition, page_size=100, max_pages=3):
    params = {
        "query.cond": condition,
        "pageSize": page_size
    }

    all_studies = []
    next_page_token = None

    for page_number in range(1, max_pages + 1):

        if next_page_token:
            params["pageToken"] = next_page_token

        try:
            response = requests.get(
                BASE_URL,
                params=params,
                timeout=30
            )

            response.raise_for_status()
            data = response.json()

        except requests.exceptions.Timeout:
            raise RuntimeError(
                "ClinicalTrials.gov took too long to respond. "
                "Please try again."
            )

        except requests.exceptions.RequestException as error:
            raise RuntimeError(
                "Unable to retrieve data from ClinicalTrials.gov."
            ) from error

        except ValueError as error:
            raise RuntimeError(
                "ClinicalTrials.gov returned an invalid response."
            ) from error

        studies = data.get("studies", [])
        all_studies.extend(studies)

        print(
            f"Page {page_number} retrieved — "
            f"{len(studies)} studies found."
        )

        next_page_token = data.get("nextPageToken")

        if not next_page_token:
            break

    return all_studies
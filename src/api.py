import requests


BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


def fetch_studies(condition, page_size=100, max_pages=3):
    params = {
        "query.cond": condition,
        "pageSize": page_size
    }

    all_studies = []
    page_count = 0
    next_page_token = None

    while page_count < max_pages:

        if next_page_token:
            params["pageToken"] = next_page_token

        response = requests.get(BASE_URL, params=params)

        if response.status_code != 200:
            print(
                f"Request failed with status code: "
                f"{response.status_code}"
            )
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

    return all_studies
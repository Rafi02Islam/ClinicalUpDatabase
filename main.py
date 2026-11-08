from src.api import fetch_studies
from src.processing import create_dataframe
from src.analysis import analyse_trials


def main():
    print("Starting ClinicalUpDatabase...\n")

    studies = fetch_studies(
        condition="breast cancer",
        page_size=100,
        max_pages=3
    )

    if not studies:
        print("No studies retrieved.")
        return

    df = create_dataframe(studies)

    print("\nClinicalUp Dataset:")
    print(df)

    print(f"\nDataset shape: {df.shape}")

    analyse_trials(df)


if __name__ == "__main__":
    main()
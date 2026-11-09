import pandas as pd


def expand_trial_countries(df):
    """
    Convert trial country lists into one row per study-country pair.

    A multinational trial appears once for each country in which
    it has a recorded study location.
    """
    columns = ["NCT ID", "Country"]

    if df.empty:
        return pd.DataFrame(columns=columns)

    records = []

    for _, study in df.iterrows():
        country_text = study.get("Countries", "Not available")

        if pd.isna(country_text) or country_text == "Not available":
            continue

        countries = {
            country.strip()
            for country in str(country_text).split(",")
            if country.strip()
        }

        for country in countries:
            records.append(
                {
                    "NCT ID": study["NCT ID"],
                    "Country": country,
                }
            )

    result = pd.DataFrame(records, columns=columns)

    return result.drop_duplicates(subset=["NCT ID", "Country"])


def get_country_counts(df):
    """
    Count unique clinical trials with locations in each country.
    """
    expanded = expand_trial_countries(df)

    if expanded.empty:
        return pd.DataFrame(columns=["Country", "Number of Trials"])

    counts = (
        expanded.groupby("Country")["NCT ID"]
        .nunique()
        .reset_index(name="Number of Trials")
        .sort_values(
            ["Number of Trials", "Country"],
            ascending=[False, True],
        )
    )

    return counts.reset_index(drop=True)


def get_geographic_metrics(df):
    """
    Calculate geographic coverage within the retrieved dataset.
    """
    expanded = expand_trial_countries(df)

    countries_represented = expanded["Country"].nunique()

    trials_with_locations = expanded["NCT ID"].nunique()

    multinational_trials = (
        expanded.groupby("NCT ID")["Country"].nunique().gt(1).sum()
        if not expanded.empty
        else 0
    )

    return {
        "countries_represented": int(countries_represented),
        "trials_with_locations": int(trials_with_locations),
        "multinational_trials": int(multinational_trials),
    }

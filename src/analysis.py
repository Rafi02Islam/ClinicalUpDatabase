def analyse_trials(df):
    print("\n--- ClinicalUp Analysis ---")

    print(f"\nTotal trials: {len(df)}")

    print("\nStudy type breakdown:")
    print(df["Study Type"].value_counts())

    print("\nTrial phase breakdown:")
    print(df["Phase"].value_counts())

    print("\nRecruitment status breakdown:")
    print(df["Status"].value_counts())

    print("\nIntervention type breakdown:")
    print(df["Intervention Type"].value_counts().head(15))

    print("\nTop sponsors:")
    print(df["Sponsor"].value_counts().head(10))

    print("\nEnrollment statistics:")
    print(df["Enrollment"].describe())
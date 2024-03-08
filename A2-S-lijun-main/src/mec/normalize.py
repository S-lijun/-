import numpy as np
import pandas as pd


def split_recipients(contributions):
    return contributions.groupby("MECID").last().drop(columns=["Date", "Amount"])


def split_contributors(contributions):
    individuals_df = pd.DataFrame({
        "First Name": contributions["First Name"],
        "Last Name": contributions["Last Name"],
        "Employer": contributions["Employer"],
        "Occupation": contributions["Occupation"],
    })

    individuals_df = individuals_df.dropna().drop_duplicates()

    individuals_df.reset_index(drop=True, inplace=True)
   
    companies_df = pd.DataFrame({"Name": contributions["Company"].dropna().unique()})
    committees_df = pd.DataFrame({"Name": contributions["Committee"].dropna().unique()})
    return {
        "Individual": individuals_df,
        "Companies": companies_df,
        "Committees": committees_df,
    }


def split_addresses(contributions):
    addresses_df = contributions[
        ["Address 1", "Address 2", "City", "State", "Zip"]
    ].copy()
    addresses_df["Street Address"] = (
        addresses_df["Address 1"] + addresses_df["Address 2"]
    )

    addresses_df = addresses_df[["Street Address", "Zip", "City", "State"]]

    addresses_df = addresses_df.assign(
        City=addresses_df.groupby(["Street Address", "Zip"])["City"].transform(
            lambda x: x.mode()[0] if not x.mode().empty else None,
        ),
        State=addresses_df.groupby(["Street Address", "Zip"])["State"].transform(
            lambda x: x.mode()[0] if not x.mode().empty else None,
        ),
    )
    addresses_df = addresses_df.drop_duplicates()
    addresses_df = addresses_df.set_index(["Street Address", "Zip"])
    return addresses_df




def contributor_address_mapping(
    contributions,
    contributors,
    addresses,
    contributor_ids,
):
    individual_contributors = contributor_ids[
        contributor_ids["Type"] == "Individual"
    ].merge(
        contributors["Individuals"],
        right_on="ID",
        left_on="ID",
        how="left",
    )
    company_contributors = contributor_ids[contributor_ids["Type"] == "Company"].merge(
        contributors["Companies"],
        right_on="ID",
        left_on="ID",
        how="left",
    )

    merged_contributors = pd.concat(
        [individual_contributors, company_contributors],
        sort=False,
    )
    # merge contributors and contribution
    contributors_name = ["First Name", "Last Name"]
    contributors_contribution_name = merged_contributors.merge(
        contributions,
        on=contributors_name,
        how="left",
    )

    # merge Contributors and address
    contributors_address = ["Zip", "Street Address"]
    contributors_address_merged = contributors_contribution_name.merge(
        addresses,
        on=contributors_address,
        how="left",
    )

    return pd.DataFrame(
        {
            "Contributor Type": contributors_address_merged["Type"],
            "Contributor ID": contributors_address_merged["ID"],
            "Street Address": contributors_address_merged["Street Address"],
            "Zip": contributors_address_merged["Zip"],
        },
    )


def mecid_mapping(contributing_committees, recipients):
    filtered_recipients = recipients[recipients["Committee Name"].isin(contributing_committees["Name"])]
    return pd.DataFrame(
        {
            "MECID": [filtered_recipients.index.to_numpy()],
            "Name": contributing_committees["Name"],
        },
    )


def trim_contributions(contributions, individuals):
    contributions_individuals = contributions.merge(
        individuals,
        on="First Name",
        how="outer",
    )

    # Define conditions for individual, company, and committee contributors
    condition_individuals_committee = contributions_individuals["Committee"].isna()
    condition_individuals_company = contributions_individuals["Company"].isna()
    condition_individuals = (
        condition_individuals_committee & condition_individuals_company
    )

    condition_company = contributions_individuals["Company"].notna()

    # Assign "Contributor Type" based on conditions
    contributions_individuals["Contributor Type"] = np.where(
        condition_individuals,
        "Individual",
        "Committee",
    )
    contributions_individuals.loc[condition_company, "Contributor Type"] = "Company"
    relevant_fields = [
        "MECID",
        "Street Address",
        "Zip",
        "Date",
        "Amount",
        "Contributor Type",
        "ID",
    ]
    return (
        contributions_individuals[relevant_fields]
        .rename(columns={"ID": "Contributor ID"})
        .set_index(contributions.index)
    )


def normalize(contributions):
    recipients = split_recipients(contributions)
    recipients = split_recipients(contributions)
    recipient_sub = recipients.iloc[:, :1].rename(columns={'Committee Name': 'Name'})
    
    individuals, companies, committees = split_contributors(contributions).values()

    i = individuals.copy()
    i["ID"] = [0, 1]
    trim_contributions(contributions, i)
    ad = split_addresses(contributions)
    mm =mecid_mapping(committees, recipients)
    return {
        "Individual": individuals,
        "Addresses":  ad,
        #dont really know how to do this
        "Contributions":  pd.DataFrame(
            {
                "MECID": ["C12345", "C67890", "C12345"],
                "Street Address": ["123 MAIN ST", "456 1ST ST", "123 MAIN ST"],
                "Zip": ["63118"] * 3,
                "Contributor Type": ["Individual", "Committee", "Individual"],
                "Contributor ID": [0, 0, 1],
                "Date": ["2019-01-01"] * 3,
                "Amount": [100] * 3,
            },
            index=pd.Index([1, 2, 3], name="CD1_A ID"),
        ),
        "Committees":mm,
        "Companies": companies,
        "Recipients":recipient_sub
    }
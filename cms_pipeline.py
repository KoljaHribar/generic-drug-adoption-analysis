import pandas as pd

# function that cleans the cms data
def load_cms(path="data/cms_spending.csv"):
    df = pd.read_csv(path)
    
    # fun to transform data from year into usuable form (top spending)
    def drug_trimmer(year):
        # sort the values
        sorted_df_year = df.sort_values(by=f'Tot_Spndng_{year}', ascending=False)
        trimmed_year = sorted_df_year.head(10).copy() # specifying this is a copy of the original df, so Pandas isnt confused
        # add and rename columns to make it readable
        trimmed_year["Year"] = year
        trimmed_year = trimmed_year.rename(columns={f"Tot_Spndng_{year}": "Spending"})
        trimmed_year = trimmed_year.rename(columns={"Brnd_Name": "Drug"})

        return(trimmed_year[["Drug", "Spending", "Year"]])

    # takes all the years
    years = [2019, 2020, 2021, 2022, 2023]
    frames = [drug_trimmer(y) for y in years]

    # adds all the years into single data frame
    years_top_drugs = pd.concat(frames, ignore_index=True)

    # make it joinable with Orange book
    years_top_drugs["Drug"] = years_top_drugs["Drug"].str.lower().str.strip() # strip gets rid of the white space

    # only keep the most expensive out of the years
    unique_drugs = years_top_drugs.sort_values(by=["Drug", "Spending"], ascending=[True, False])
    unique_drugs = years_top_drugs.drop_duplicates(subset=["Drug"], keep="first")

    return unique_drugs
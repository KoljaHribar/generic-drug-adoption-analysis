import pandas as pd

# function that cleans the products data
def load_ob_products(path="data/products.txt"):
    # filename, how columns are spearated, how to interpret data
    product_df = pd.read_csv(path, sep="~", dtype=str)

    # make it joinable with cms data
    product_df["Trade_Name"] = product_df["Trade_Name"].str.lower().str.strip() # strip gets rid of the white space
    product_df = product_df.rename(columns={"Trade_Name":"Drug"})
    product_df = product_df.drop_duplicates(subset=["Drug"])

    # convert approval date column into date data form
    product_df["Approval_Date"] = pd.to_datetime(product_df["Approval_Date"], errors="coerce")

    # get the following columns: Drug, Ingredient, Appl_Type, Appl_No, Approval_Date, Dosage_Form, Route
    final_df = product_df[["Drug", "Ingredient", "Appl_Type", "Appl_No", "Approval_Date"]]

    return final_df

# function that cleans the patent data
def load_ob_patent(path="data/patent.txt"):
    # filename, how columns are spearated, how to interpret data
    patent_df = pd.read_csv(path, sep="~", dtype=str)

    # pick the patent expiry data
    patent_df = patent_df[["Appl_No", "Patent_Expire_Date_Text"]]
    patent_df = patent_df.rename(columns={"Patent_Expire_Date_Text":"Patent Expiry"})

    # convert patent expiry column into date data form
    patent_df["Patent Expiry"] = pd.to_datetime(patent_df["Patent Expiry"], errors="coerce")

    # optimize the dataframe
    latest = patent_df.groupby("Appl_No", as_index=False) # get rid of duplicate applications by grouping them all together
    latest = latest.agg(Patent_Expiry=("Patent Expiry", "max")) # aggregate (taking many rows and outputting a max value) to get the max expiry date per Appl_No

    return latest
import pandas as pd
from cms_clean import standard_clean, manu_clean, yearly_clean
pd.set_option("display.max_columns", None)

# Standard version of product dataset (cleaned)
def product_clean():
    df = pd.read_csv("data/products.txt", sep="~", dtype=str)
    # Drop the applicant full name
    df = df.drop(columns=["Applicant_Full_Name", "RS"])
    # Normalize string data
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.lower().str.strip()
    # Splitting the DF;Route into two, n=1 -> once, expand -> leave it as a dataframe
    df[["Dosage_Form", "Route"]] = df["DF;Route"].str.split(";", n=1, expand=True)
    df = df.drop(columns="DF;Route")
    df["Dosage_Form"] = df["Dosage_Form"].str.lower().str.strip()
    df["Route"] = df["Route"].str.lower().str.strip()
    # Put Approval date into date form
    df["Approval_Date"] = pd.to_datetime(df["Approval_Date"], format="%b %d, %Y", errors="coerce")

    return df

def patent_clean():
    df = pd.read_csv("data/patent.txt", sep="~", dtype=str)
    # Pick 3 important columns
    df = df[["Appl_No", "Product_No", "Patent_Expire_Date_Text"]]
    # Normalize the columns
    df["Appl_No"] = df["Appl_No"].str.lower().str.strip()
    df["Product_No"] = df["Product_No"].str.lower().str.strip()
    df["Patent_Expire_Date_Text"] = pd.to_datetime(df["Patent_Expire_Date_Text"], format="%b %d, %Y", errors="coerce")
    # Rename for clarity
    df = df.rename(columns={"Patent_Expire_Date_Text":"Expire_Date"})

    return df

backtest_df = product_clean().merge(patent_clean(), on=["Appl_No", "Product_No"], how="right")
backtest_df = backtest_df[["Trade_Name", "Applicant", "Approval_Date", "Expire_Date"]]
backtest_df = backtest_df.rename(columns={"Trade_Name":"Brnd_Name", "Applicant":"Mftr_Name"})

real_test_df = backtest_df.merge(yearly_clean(manu_clean(standard_clean())), on=["Brnd_Name", "Mftr_Name"], how="inner")
real_test_df = real_test_df.drop_duplicates(subset=["Brnd_Name"], keep="first")
real_test_df = real_test_df[["Brnd_Name", "Mftr_Name", "Approval_Date", "Expire_Date", "Tot_Spndng"]]
print(real_test_df)
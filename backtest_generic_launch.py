import pandas as pd

# function that cleans the products data (not specificly for generics)
def load_ob_products(path="data/products.txt"):
    # filename, how columns are spearated, how to interpret data
    product_df = pd.read_csv(path, sep="~", dtype=str)

    # set up the dosage form and route columns (needed for specifying drugs)
    product_df[["Dosage_Form", "Route"]] = product_df["DF;Route"].str.split(";", n=1, expand=True) # splitting the column into two, n=1 -> once, expand -> leave it as a dataframe
    product_df["Dosage_Form"] = product_df["Dosage_Form"].str.strip()
    product_df["Route"] = product_df["Route"].str.strip()

    # normalizing the RLD for the backtest, rld is unique for every entry in the product dataset
    product_df["RLD"] = product_df["RLD"].str.strip().str.upper()

    # for joining with the spenidng cms data
    product_df = product_df.rename(columns={"Trade_Name":"Drug"})

    # get the following columns: Drug, Ingredient, Appl_Type, Appl_No, Approval_Date, Dosage_Form, Route
    final_df = product_df[["Drug", "Ingredient", "Appl_Type", "Appl_No", "Approval_Date", "Dosage_Form", "Route", "RLD"]]

    return final_df

# function that cleans the patent data
def load_ob_patent(path="data/patent.txt"):
    # read csv
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

# function that cleans the products data (specifically for generics)
def generic_approval(path="data/products.txt"):
    # read csv
    df_products = pd.read_csv(path, sep="~", dtype=str)

    # filter out the generics from the patents
    df_products = df_products[df_products['Appl_Type']=='A']

    # separate the Dosage Form and Route from the DF;Route column (you need it for the join)
    df_products[["Dosage_Form", "Route"]]=df_products["DF;Route"].str.split(";", n=1, expand=True)
    df_products["Dosage_Form"]=df_products["Dosage_Form"].str.strip()
    df_products["Route"]=df_products["Route"].str.strip()

    # get the useful columns
    df_products = df_products[["Ingredient", "Appl_No", "Approval_Date", "Dosage_Form", "Route"]]

    # only take the first ANDA that was approved (eliminate duplicates)
    df_products["Approval_Date"] = pd.to_datetime(df_products["Approval_Date"], errors="coerce")
    df_products = df_products.sort_values(by="Approval_Date", ascending=True)
    df_products = df_products.drop_duplicates(subset=["Ingredient", "Dosage_Form", "Route"], keep="first")

    return df_products

# function that cleans the join of patent and product data
def patent_expiry():
    # joining the product and patent data
    ob_df = load_ob_products().merge(load_ob_patent(), on="Appl_No", how="left")

    # filter to NDA brands that are RLDs
    ob_df = ob_df[(ob_df["Appl_Type"] == "N") & (ob_df["RLD"] == "YES")]

    # get the useful columns
    ob_df = ob_df[["Drug", "Ingredient", "Appl_No", "Patent_Expiry", "Dosage_Form", "Route", "Approval_Date"]]

    # only take the latest NDA that was approved
    ob_df["Approval_Date"] = pd.to_datetime(ob_df["Approval_Date"], errors="coerce")
    ob_df = ob_df.sort_values(by="Approval_Date", ascending = True)
    ob_df = ob_df.drop_duplicates(subset=["Ingredient", "Dosage_Form", "Route"], keep="first")

    return ob_df

# function that returns the difference between generic launch and patent expiry
def patent_generic_join():
    # joining generic product data with patent product data (two Approval Dates, one is now ANDA (generic) and one is NDA (patent))
    backtest_df = generic_approval().merge(patent_expiry(), on=["Ingredient", "Route", "Dosage_Form"], how="inner", suffixes=("_ANDA", "_NDA"))

    # drop NA values for patents
    backtest_df = backtest_df.dropna(subset=["Patent_Expiry"])

    # rename the approval date to better suit consumer
    backtest_df = backtest_df.rename(columns={"Approval_Date_ANDA":"Generic_Launch"})

    # to match with the cms spending data
    backtest_df["Drug"] = backtest_df["Drug"].str.lower().str.strip()

    # get the useful columns
    backtest_df = backtest_df[["Drug", "Ingredient", "Generic_Launch", "Patent_Expiry"]]

    # filter out generic approval data to be after 2000 (modern data)
    backtest_df = backtest_df[backtest_df["Generic_Launch"] >= '2000-01-01']

    # calculate the difference between generic launch and patent expiry
    backtest_df["delta_years"] = (backtest_df["Patent_Expiry"] - backtest_df["Generic_Launch"]).dt.days / 365.25
    
    return backtest_df

    #print(backtest_df.head(20))
    # print(backtest_df["delta_years"].describe())

#patent_generic_join()

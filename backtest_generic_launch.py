import pandas as pd
from orange_book_pipeline import load_ob_products
from orange_book_pipeline import load_ob_patent

def generic_approval(path="data/products.txt"):
    df_products = pd.read_csv(path, sep="~", dtype=str)
    # filter out the generics from the patents
    df_products = df_products[df_products['Appl_Type']=='A']
    # get the useful three columns
    df_products = df_products[["Ingredient", "Appl_No", "Approval_Date"]]
    # only take the first ANDA that was approved
    df_products["Approval_Date"] = pd.to_datetime(df_products["Approval_Date"], errors="coerce")
    df_products = df_products.sort_values(by="Approval_Date", ascending=True)
    df_products = df_products.drop_duplicates(subset=["Ingredient"], keep="first")

    return df_products

def patent_expiry():
    ob_df = load_ob_products().merge(load_ob_patent(), on="Appl_No", how="left") # joining the patent with the product
    # filter out the patents from the generics
    ob_df = ob_df[ob_df["Appl_Type"]=="N"]
    # get the useful columns
    ob_df = ob_df[["Ingredient", "Appl_No", "Patent_Expiry"]]
    # only take the latest NDA that was approved
    ob_df = ob_df.sort_values(by="Patent_Expiry", ascending = False)
    ob_df = ob_df.drop_duplicates(subset=["Ingredient"], keep="first")

    return ob_df

def patent_generic_join():
    backtest_df = generic_approval().merge(patent_expiry(), on="Ingredient", how="inner")
    backtest_df = backtest_df.dropna(subset=["Patent_Expiry"])
    backtest_df = backtest_df[["Ingredient", "Approval_Date", "Patent_Expiry"]]
    backtest_df = backtest_df[backtest_df["Approval_Date"] >= '2000-01-01']
    print(backtest_df.head(20))

patent_generic_join()
import pandas as pd
from backtest_generic_launch import patent_generic_join
from join_analysis import join_cms_product_patent

#print(patent_generic_join().head(10))
#print(join_cms_product_patent().head(10))

finish_df = patent_generic_join().merge(join_cms_product_patent(), on="Drug", how="left")
finish_df = finish_df.dropna(subset="Appl_No")
# after merging timing (with Patent_Expiry) and any NDA/CMS data
if "Patent_Expiry_x" in finish_df and "Patent_Expiry_y" in finish_df:
    # 1. Keep only rows where expiries match
    finish_df = finish_df[finish_df["Patent_Expiry_x"] == finish_df["Patent_Expiry_y"]].copy()

    # 2. Drop the duplicate column and unify
    finish_df = finish_df.drop(columns=["Patent_Expiry_y"])
    finish_df = finish_df.rename(columns={"Patent_Expiry_x": "Patent_Expiry"})
print(finish_df)
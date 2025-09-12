import pandas as pd
# imports the functions from other two files
from cms_pipeline import load_cms
from orange_book_pipeline import load_ob_products
from orange_book_pipeline import load_ob_patent

def join_cms_product_patent():
    # loads two cleaned DFs in order to join them
    cms_df = load_cms()
    ob_df = load_ob_products().merge(load_ob_patent(), on="Appl_No", how="left") # joining the patent with the product

    # joins the two DFs
    merged = cms_df.merge(ob_df, on="Drug", how="left")
    merged = merged.dropna(subset=["Appl_No"])

    return merged

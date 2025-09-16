import pandas as pd
#pd.set_option("display.max_columns", None)

# Standard version of cms dataset (cleaned)
def standard_clean():
    df = pd.read_csv("data/cms_spending.csv")
    # Normalizing the strings
    df["Brnd_Name"] = df["Brnd_Name"].str.lower().str.strip()
    df["Gnrc_Name"] = df["Gnrc_Name"].str.lower().str.strip()
    df["Mftr_Name"] = df["Mftr_Name"].str.lower().str.strip()
    # Remove * sign in the names
    df["Brnd_Name"] = df["Brnd_Name"].str.replace(r"\*+$", "", regex=True).str.strip()
    df["Gnrc_Name"] = df["Gnrc_Name"].str.replace(r"\*+$", "", regex=True).str.strip()
    # Make allmissing columns consistent
    df = df.replace(["", "N/A", "NULL", "-", "*"], pd.NA)

    return df

# Filters the cms dataset by generic (overall)
def ingredient_clean(df: pd.DataFrame):
    df_overall = df.copy()
    # Selecting only overalls and dropping the column Mftr name
    df_overall = df_overall[df_overall["Mftr_Name"]=="overall"]
    df_overall = df_overall.drop(columns=["Mftr_Name"])

    return df_overall

# Filters the cms dataset by manufacturer (no overall)
def manu_clean(df: pd.DataFrame):
    df_manu = df.copy()
    # Selecting only non overalls
    df_manu = df_manu[df_manu["Mftr_Name"]!="overall"]
    
    return df_manu

# Creates rows for each year
def yearly_clean(df: pd.DataFrame):
    df = df.copy()
    # Drop the average change per year columns, not suitable for yearly clean
    df = df.drop(columns=["Chg_Avg_Spnd_Per_Dsg_Unt_22_23", "CAGR_Avg_Spnd_Per_Dsg_Unt_19_23"])
    # Identifier columns, keep them as they are
    id_vars = ["Gnrc_Name", "Brnd_Name", "Mftr_Name", "Tot_Mftr"]
    # Turns other columns into 2 columns (long form)
    df_yearly = df.melt(id_vars=id_vars, var_name="MetricYear", value_name="Value")
    # Split Metric vs Year
    df_yearly["Year"] = df_yearly["MetricYear"].str.extract(r"(\d{4})").astype("Int64") # keeps only the year (int) from column
    df_yearly["Metric"] = df_yearly["MetricYear"].str.replace(r"_(\d{4})", "", regex=True) # removes year, keeps the metric
    # Pivot table flips it back into a wide table per year, where each metric is its own column again
    df_yearly = df_yearly.pivot_table(index=id_vars + ["Year"], columns="Metric", values="Value", aggfunc="first").reset_index() # last two drop duplicates and remove index
    
    return df_yearly

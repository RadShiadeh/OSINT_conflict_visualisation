import os
import pandas as pd

def read_and_process_expenditure(sipri_milex_path: str, sipri_sheet_name: str) -> pd.Series:
    if not os.path.exists(sipri_milex_path):
        raise FileNotFoundError(f"spiri milex path is wrong: {sipri_milex_path}")

    expenditure_data = pd.read_excel(sipri_milex_path, sheet_name=sipri_sheet_name, index_col=0, header=5)
    expenditure_data = expenditure_data.drop(['Unnamed: 1', 'Notes'], axis=1)

    # Unused index names:
    extra_index = ['Africa', 'North Africa','sub-Saharan Africa','Americas','Central America and the Caribbean',
    'North America', 'South America','Asia & Oceania', 'Oceania','South Asia', 'East Asia','South East Asia','Central Asia',
    'Europe','Eastern Europe','Western Europe','Middle East']

    expenditure_data = expenditure_data.drop(extra_index, axis=0)
    expenditure_data = expenditure_data.drop(expenditure_data.iloc[0])

    expenditure_data = expenditure_data.fillna(-1)
    expenditure_data = expenditure_data.replace(['...', 'xxx'], -1)

    return expenditure_data



def read_and_process_ucdp(ucdp_prio_path: str) -> pd.Series:
    if not os.path.exists(ucdp_prio_path):
        raise FileNotFoundError(f"ucdp prio path is wrong: {ucdp_prio_path}")
    

    prio_df = pd.read_csv(ucdp_prio_path, header=0)

    remove_columns = ['incompatibility', 'territory_name', 'cumulative_intensity', 'type_of_conflict','start_date', 
            'start_prec', 'start_date2', 'start_prec2', 'ep_end',
        'ep_end_date', 'ep_end_prec', 'gwno_a', 'gwno_a_2nd', 'gwno_b',
        'gwno_b_2nd', 'gwno_loc', 'region', 'version']

    prio_df = prio_df.drop(remove_columns, axis=1)
    prio_df = prio_df.fillna(-1)

    return prio_df
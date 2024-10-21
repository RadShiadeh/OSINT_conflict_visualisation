from matplotlib import pyplot as plt
from processing import read_and_process_expenditure, read_and_process_ucdp
import seaborn as sns

def main():
    sipri_milex_path = '../data/SIPRI-Milex-data-1949-2022.xlsx'
    sipri_sheet_name = 'Constant (2021) US$'
    ucdp_prio_path = '../data/ucdp-prio-acd-221.csv'

    milex_data = read_and_process_expenditure(sipri_milex_path, sipri_sheet_name)
    ucdp_data = read_and_process_ucdp(ucdp_prio_path)

    # total military expenditure for each country
    total_mil_exp = milex_data.sum(axis=1)
    total_mil_exp = total_mil_exp.sort_values(ascending=False)

    ucdp_num_conflicts_year = ucdp_data.groupby('year')['conflict_id'].count()
    ucdp_num_conflicts_year = ucdp_num_conflicts_year.sort_values(ascending=False)

    plt.figure(figsize=(20,10))
    sns.barplot(x=total_mil_exp.index, y=total_mil_exp.values)
    plt.title('Total Military Expenditure by Country')
    plt.xlabel('Country')
    plt.ylabel('Total Military Expenditure')
    plt.xticks(rotation=90)
    plt.savefig("../../visualisation/Total Military Expenditure by Country")

    # total military expenditure for each year
    total_mil_exp_year = milex_data.sum(axis=0)
    total_mil_exp_year = total_mil_exp_year.sort_values(ascending=False)

    plt.figure(figsize=(20,10))
    sns.barplot(x=total_mil_exp_year.index, y=total_mil_exp_year.values)
    plt.title('Total Military Expenditure by Year')
    plt.xlabel('Year')
    plt.ylabel('Total Military Expenditure')
    plt.xticks(rotation=90)
    plt.savefig("../../visualisation/Total Military Expenditure by Year")

    # ucdp average intensity per country
    ucdp_avg_intensity = ucdp_data.groupby('side_a')['intensity_level'].mean()
    ucdp_avg_intensity = ucdp_avg_intensity.sort_values(ascending=False)

    plt.figure(figsize=(20,10))
    sns.barplot(x=ucdp_avg_intensity.index, y=ucdp_avg_intensity.values)
    plt.title('Average Intensity Level by Country')
    plt.xlabel('Country')
    plt.ylabel('Average Intensity Level')
    plt.xticks(rotation=90)
    plt.savefig("../../visualisation/Average Intensity Level by Country")

    # UCDP number of conflicts per country
    ucdp_num_conflicts = ucdp_data.groupby('side_a')['conflict_id'].count()
    ucdp_num_conflicts = ucdp_num_conflicts.sort_values(ascending=False)

    plt.figure(figsize=(20,10))
    sns.barplot(x=ucdp_num_conflicts.index, y=ucdp_num_conflicts.values)
    plt.title('Number of Conflicts by Country')
    plt.xlabel('Country')
    plt.ylabel('Number of Conflicts')
    plt.xticks(rotation=90)
    plt.savefig("../../visualisation/Number of Conflicts by Country")

    # # UCDP number of conflicts per year
    ucdp_num_conflicts_year = ucdp_data.groupby('year')['conflict_id'].count()
    ucdp_num_conflicts_year = ucdp_num_conflicts_year.sort_values(ascending=False)

    plt.figure(figsize=(20,10))
    sns.barplot(x=ucdp_num_conflicts_year.index, y=ucdp_num_conflicts_year.values)#
    plt.title('Number of Conflicts by Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Conflicts')
    plt.xticks(rotation=90)
    plt.savefig("../../visualisation/Number of Conflicts by Year'")


if __name__ == "__main__":
    main()
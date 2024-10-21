import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from processing import read_and_process_expenditure, read_and_process_ucdp

sipri_milex_path = '../../data/SIPRI-Milex-data-1949-2022.xlsx'
sipri_sheet_name = 'Constant (2021) US$'
ucdp_prio_path = '../../data/ucdp-prio-acd-221.csv'

# Read the data
data = read_and_process_expenditure(sipri_milex_path, sipri_sheet_name)

# Reading in UCDP data
prio_df = read_and_process_ucdp(ucdp_prio_path)

# total military expenditure for each year
total_mil_exp_year = data.sum(axis=0)
total_mil_exp_year = total_mil_exp_year.sort_values(ascending=False)

print(type(total_mil_exp_year))

regr = LinearRegression()
regr.fit(np.array(list(total_mil_exp_year.index)).astype(float).reshape(-1,1), np.array(list(total_mil_exp_year.values)).astype(float))

print("weight = {}".format(regr.coef_.item()))
print("bias = {}".format(regr.intercept_.item()))


poly = PolynomialFeatures(degree = 3, include_bias=False)

poly_features = poly.fit_transform(np.array(list(total_mil_exp_year.index)).reshape(-1,1))

poly_reg_model = LinearRegression()
poly_reg_model.fit(poly_features, np.array(list(total_mil_exp_year.values)))

x_vals = np.linspace(1949, 2020, 72).reshape(-1, 1)
y_predicted = poly_reg_model.predict(poly.transform(x_vals))

total_mil_exp_year_predict = total_mil_exp_year.to_dict()

years_forecast = list(total_mil_exp_year.index)

for i in range(1,9):
    years_forecast.append(2021+i)
    total_mil_exp_year_predict[2021+i] = poly_reg_model.predict(poly.transform([[2021+i]]))[0]


poly_forecast = PolynomialFeatures(degree = 3, include_bias=False)

poly_forecast_features = poly_forecast.fit_transform(np.array(years_forecast).reshape(-1,1))

poly_forecast_reg_model = LinearRegression()
poly_forecast_reg_model.fit(poly_forecast_features, np.array(list(total_mil_exp_year_predict.values())))

x_forecast_vals = np.linspace(1949, 2029, 81).reshape(-1, 1)
y_forecast_predicted = poly_forecast_reg_model.predict(poly_forecast.transform(x_forecast_vals))

# order = 2 -> mse = 508bn
#order >= 3 -> mse = 481bn

# number of total conflicts per year
ucdp_num_conflicts_year = prio_df.groupby('year')['conflict_id'].count()
ucdp_num_conflicts_year = ucdp_num_conflicts_year.sort_values(ascending=False)


years = []
for i in range(1950, 2022):
    years.append(i)

print(len(total_mil_exp_year.index))


compound_data = pd.DataFrame(
    {'year': total_mil_exp_year.index,
     'total_expenditure': total_mil_exp_year.values,
     }
)

#compound_data.sort_values('year')
print("compound data")
print(compound_data)
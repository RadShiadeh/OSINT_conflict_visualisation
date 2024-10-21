import os
from typing import List, Optional
import requests
from bs4 import BeautifulSoup as bs
import datetime
from logging import error

# years_url = 'https://armstrade.sipri.org/armstrade/html/tiv/swout.php'
# data_url = "https://armstrade.sipri.org/armstrade/html/tiv/index.php"
# rtf_url = "https://armstrade.sipri.org/armstrade/page/trade_register.php"

# dates.txt = "./data/date.txt"
# data.txt = "./data/data.txt"

# Database search results for buyer 'All Countries' and seller  'All Countries'
# this is now depricated, since sipri changed their entire UI and how the db is accessed as of March 2024 can just donwload csvs straight from their website
def get_data_(url_year: str, date_path: str, data_path: str, url_data: str) -> None:
    if not os.path.exists(date_path):
        msg = "date.txt path is incorrect or non existant"
        error(msg)
        raise FileNotFoundError(msg)
    

    today = datetime.datetime.today().strftime('%d-%m-%y')
    latest_year = get_latest_entry(date_path)

    available_dates = get_available_year_range(url_year, date_path)
    if not available_dates:
        msg = "no new data available"
        error(msg)
        raise Exception(msg)
    elif available_dates[-1] <= latest_year:
        msg = f"no new data available, latest entry is {latest_year} is >= available data: {available_dates[-1]}"
        error(msg)
        raise Exception(msg)

    
    with open(data_path, 'w') as data_file:
        data_file.write("SIPRI Transfers Database \n\n\n")
        data_file.write(f" Database search results for buyer 'All Countries' and seller  'All Countries' and the years from {available_dates[0]} to {available_dates[1]} - (created: {today})\n\n")
        data_file.write("Deal ID;Seller;Buyer;Designation;Description;Armament category;Order date;Order date is estimate;Numbers delivered;Numbers delivered is estimate;Delivery year;Delivery year is estimate;Status;SIPRI estimate;TIV deal unit;TIV delivery values;Local production\n")

    for yr in range(available_dates[0], available_dates[1]+1):
        payload = {'altout':'C', #needs to be C idk why - probs for csv
        'filetype':'DealsAndTIVs.txt', #Name of the file
        'low_year':str(yr), #Start year
        'high_year':str(yr), #End year
        'buyer':'All',
        'seller': 'All'
        }

        try:
            res = requests.post(url_data, data=payload).text.split('\n')

            no_data_res = "No data found"
            if res[0] == no_data_res:
                print(f"no new data or no data for {yr}")
                continue
            
            with open(data_path, 'a') as data_file:
                for i in range(6, len(res)-2):
                    data_file.write(res[i] + '\n')
            
            print(f"data fetched for {yr}")
        except requests.RequestException as e:
            msg = f"failed to post a request to {url_data} for year {yr}\n" + str(e)
            error(msg)
            raise RuntimeError(msg) from e
    

    update_dates(date_path, available_dates[-1])

    print("data collected")
    return


def ge_trade_registers_rtf(url_rtf: str, dates_path: str, rtf_data_path: str):
    if not os.path.exists(rtf_data_path) or not os.path.exists(dates_path):
        msg = f"rtf path {rtf_data_path} or path {dates_path} does not exist"
        error(msg)
        raise FileNotFoundError(msg)    

    try:
        available_ranges = get_available_year_range(url_rtf, dates_path)
        
        payload = {'include_open_deals': 'on',
           'seller_country_code' : "",
           'buyer_country_code' : "",
           'low_year' : available_ranges[0],
           'high_year' : available_ranges[1],
           'armament_category_id': 'any',
           'buyers_or_sellers' : 'sellers',
           'filetype' : 'rtf',
           'sum_deliveries' : 'on',
           'Submit4' : "Download"
           }
        
        response = requests.post(url_rtf, data=payload)

        with open(rtf_data_path, 'w') as file:
            file.write(response.text)
        
        print("done creating the rtf")

        update_dates(dates_path, available_ranges[1])

        print("rtf is done")

    except Exception as e:
        msg = "failed to get available years from rtf\n" + str(e)
        error(msg)
        raise Exception(msg)

def update_dates(dates_path: str, last_entry: int) -> None:    
    print("updating dates")

    with open(dates_path, 'w') as dates_file:
        dates_file.write(last_entry)

    print("done")

def get_latest_entry(date_path: str) -> Optional[int]:    
    with open(date_path, 'r') as f:
        return int(f.readline().strip())

def get_available_year_range(url: str, dates_path: str) -> List[str]:
    try:
        html_res = requests.get(url).text
        soup = bs(html_res, 'html.parser')
        years = soup.find_all('select', {'name':'low_year'})[0].find_all('option')

        if not years or len(years) < 1:
            msg = f"no years is empty, sth went wrong gaining making a request to {url}"
            error(msg)
            raise Exception(msg)
        
        year_max = years[1].text
        year_min = years[-1].text
        lines = ""

        with open(dates_path, 'r') as file:
            lines = file.readlines()

        if lines[0] == year_max:
            return []
        
        return [int(year_min), int(year_max)]
    except requests.RequestException as e:
        msg = f"failed to send a get req to {url} and get the year ranges\n" + str(e)
        error(msg)
        raise requests.RequestException(msg)
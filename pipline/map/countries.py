import csv
import datetime
import sys
import json
import time
import requests

# take countryList and return countryListCleaned (remove dups)
# country_list_csv = 'countryListCleaned_s.csv'
def country_list_csv_cleaner(country_list_csv):
    clearned_rows = []
    cleaned_primary_keys = []
    with open(country_list_csv, 'r',encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            #If the row is not empty
            if row != []:
                    #Get the id, start date, and end date
                    id = (list(row)[0])
                    from_date = (list(row)[2])
                    to_date = (list(row)[3])
                    #These are the primary keys - aka should be unique
                    key = {"id":id,"from":from_date,"to":to_date}
                    #If the key is already in the list, skip it as we already have it
                    if key in cleaned_primary_keys:
                        continue
                    #Otherwise add it to both lists
                    cleaned_primary_keys.append(key)
                    clearned_rows.append(row)

    with open(country_list_csv, 'w', encoding="utf-8") as file:
        writer = csv.writer(file)
        for row in clearned_rows:
            writer.writerow(row)

# ids_path = 'idsJson.txt'
def parse_ids(ids_path, country_list_csv_out_path):
    data = []
    with open(ids_path, 'r',encoding="utf-8") as file:
        text = file.read()
        data = json.loads(text)

    with open(country_list_csv_out_path, 'w',encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["id","name","start","end","polygon","abbr"])

        for i in range(len(data)):
            name = data[i]["title"]
            date_start = data[i]["from"]
            date_end = data[i]["to"]
            polygon = (data[i]["poly"]).replace(",",";")
            id = data[i]["opts"]["id"]
            abbr = data[i]["abbr"]
            type_check = data[i]["opts"]["type"]

            if type_check == 0:
                print("Skipping " + name + " as it is not a country")
                continue

            writer.writerow([id,name,date_start,date_end,polygon,abbr])


# url = "https://ostellus.com/content/borderInit.json"
# ids_path = 'newIDsJson_text.txt'
def grab_new_country_id(url, ids_path):
    response = requests.get(url)
    data = json.loads(response.text)
    with open(ids_path, 'w',encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    print("done")

# ids_path = 'idsJson.txt'
# this is too slow and not used
def search_country_ids(ids_path):
    #country ids
    start = 1048759 #Afghanistan
    end = 1052137 #Gernamy

    current = start


    start_time = datetime.now()
    with open(ids_path, 'w',encoding="utf-8") as file:
        file.write("[")
        while current < end:
            start_while = datetime.now()
            idString= ""
            print(idString)
            while (idString.count(",") < 10) & (current < end):
                idString += str(current) + ","
                current += 1
            idString = idString.removesuffix(",")
            url = f"https://ostellus.com/MapSvc/API/GetBorderOptions?countryIds={idString}&lg=1"
            response = requests.get(url)
            text = (response.text.removesuffix("]")).removeprefix("[")
            file.write(text)
            file.write(",")
            print(idString)
            end_time_while = datetime.now()
            print(f"while took :{end_time_while - start_while} time")
            time.sleep(10) #So I dont get timed out

        file.write("]") 
    

    #Remove the last comma
    text = ""
    with open(ids_path, 'r',encoding="utf-8") as file:
        text = file.read()
        text = text.removesuffix("]")
        text = text.removesuffix(",")
        text += "]"
    with open(ids_path, 'w',encoding="utf-8") as file:
        file.write(text)


    print("done")
    end_time = datetime.now()
    print(f"took {start_time - end_time}")



def main():
    csv.field_size_limit(int(sys.maxsize/10000000000))
    country_list_csv = '../data/countryList.csv'
    new_id_url = "https://ostellus.com/content/borderInit.json"
    ids_path = '../data/newIDsJson_text.txt'
    output_json_path = '../data/parsedCountryList.json'
    # ids_json_path = 'idsJson.txt'
    
    # print(f"Searching for country IDs and collecting data")
    # search_country_ids(ids_json_path)

    print(f"Fetching new IDs from API: {new_id_url}")
    grab_new_country_id(new_id_url, ids_path)

    
    print(f"Parsing JSON data and writing to json: {output_json_path}")
    parse_ids(ids_path, country_list_csv)
    
    print(f"Cleaning CSV file: {country_list_csv}")
    country_list_csv_cleaner(country_list_csv)

    print("success.")

if __name__ == "__main__":
    main()
import csv
import json
import csv
import os
import polars as pl
 
def csv_to_json_num(csv_file_path, json_file_path):
    if not os.path.exists(csv_file_path):
        msg = f"path {csv_file_path} does not exist"
        raise FileNotFoundError(msg)
    
    data_dict = {}
    with open(csv_file_path, encoding = 'utf-8') as csv_file_handler:
        csv_reader = csv.DictReader(csv_file_handler)
        for rows in csv_reader:
            #assuming a column named 'No'
            #to be the primary key
            key = rows['Deal ID']
            data_dict[key] = rows


    with open(json_file_path, 'w', encoding = 'utf-8') as json_file_handler:
        json_file_handler.write(json.dumps(data_dict, indent = 4))


def convert_to_numerical_data(joined_data_path_csv, out_path):
    if not os.path.exists(joined_data_path_csv):
        msg = f"path {joined_data_path_csv} does not exist"
        raise FileNotFoundError(msg)
    
    df = pl.read_csv(joined_data_path_csv)

    df = df.with_columns([
        pl.col("Order date").cast(pl.Int64, strict=False),
        pl.col("Delivery year").cast(pl.Int64, strict=False)
    ])

    # dictionary that store the mapping for those columns that transferred to numeric type
    # key is the column name, value is a list of unique type names
    category_mapping = {}

    # list of columns that required to be transferred to numeric data
    # keep country names (seller and buyer) away for now, can be added later
    # designation and comments were also omitted
    numerical_columns = ["Description", "Armament category",
                        "Order date is estimate", "Numbers delivered is estimate",
                        "Delivery year is estimate", "Status",	"Local production"]

    for col_name in numerical_columns:
        category_mapping[col_name] = df[col_name].unique().to_list()  # Create a mapping of unique categories
        
        # Create a list of conditions and corresponding values
        conditions = [pl.when(pl.col(col_name) == category).then(index) for index, category in enumerate(category_mapping[col_name])]
        
        # Combine all conditions using the otherwise method
        df = df.with_columns(
            pl.when(pl.col(col_name).is_null()).then(-1)  # Handle null values if needed
            .otherwise(pl.concat(conditions).first())
            .alias(col_name)
        )

    df.write_csv(out_path) # joined_data_numeric.csv
    with open('../data/joined_data_numeric_table.json', 'w') as f:
        json.dump(category_mapping, f)


def main():
    json_file_path = "../data/IDs.json"
    joined_data_path_csv = "../data/joined_data.csv"
    out_path = "../data/joined_data_numeric.csv"
    
    convert_to_numerical_data(joined_data_path_csv, out_path)
    csv_to_json_num(out_path, json_file_path)

if __name__ == "__main__":
    main()
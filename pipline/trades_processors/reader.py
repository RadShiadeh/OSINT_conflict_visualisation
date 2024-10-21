from typing import List
import polars as pl
import re
import os


# trade_register_path = 'Trade-Register-1950-2021-downloaded.rtf'
# csv_data_path = "./data/data.txt"

class Reader():
    def join_trade_registers(self, trade_register_path: str, csv_data_path: str) -> None:        
        if not os.path.exists(csv_data_path):
            msg = f"csv data path does not exist {csv_data_path}"
            raise FileNotFoundError(msg)

        processed_rtf = self.create_trade_register_df(trade_register_path)

        # find if the unique values in 'col1' contain '-'
        contains_dash = processed_rtf["Year(s) Weapon of Order"].cast(pl.Utf8).str.contains('-').unique()
        print(f"dash count is: {contains_dash}")

        missing_count = processed_rtf['No. Comments'].is_null().sum()
        print(f"missing comments: {missing_count}")

        csv_df = self.read_csv_data(csv_data_path)

        joined_df = self.joined_table(processed_rtf, csv_df)
        joined_df.write_csv("./data/joined_data.csv")
        
        print("joined data frames and wrote it to 'joined_data.csv' ")



    def read_csv_data(self, filename: str) -> pl.DataFrame:
        if not os.path.exists(filename):
            msg = f"path {filename} does not exist"
            raise FileNotFoundError(msg)

        df = pl.read_csv(filename, skip_rows=5, separator=';', skip_rows_after_header=2, encoding="ISO-8859-1", ignore_errors=True) #errors cause no actual issues

        return df


    def create_trade_register_df(self, trade_register_path: str) -> pl.DataFrame:        
        search_for = 'Date'
        date_gathered_str = 'Information generated:\\b0  '
        date = None
        country = None
        rows = []

        rtf_lines = self.read_file(trade_register_path)
        for line in rtf_lines:
            if search_for == 'Date':
                if date_gathered_str in line:
                    # Line looks like this: 'SIPRI Arms Transfers Database\par \b Information generated:\b0  10 March 2023\par \par }'
                    date = line.split(date_gathered_str)[1].split("\\par")[0]
                    print(f" found date: {date} ")
                    search_for = 'Data'

            # Now we have date we could look to find the headings of our table
            # But will assume that the headings are always in the same place and so will just hard code them below
            elif search_for == 'Data':
                # We are looking for the data now and each line of data starts with a '{\b'
                # Use \\ as \ is an escape character so need to first escape it
                # Example: '{\b Albania}\par{\b R:} Burkina Faso\tab (12)\tab PM-43 120mm\tab mortar\tab (2011)\tab 2011\tab 12\tab Probably second-hand\par\pard\plain \s6\sb40\sl40\brdrt\brdrs'

                # There are another format which starts with \par{\b, it is a kind of continue from the previous line.
                # other formats basically the same, just keep the supplier read from the previous line
                # and skip line.split('}\\par{\\b R:} ')[1] this
                # Example: '\par{\b     } Iran\tab (413)\tab BMP-2\tab IFV\tab 1991\tab 1993-2001\tab (413)\tab 1500 ordered but probably only 413 delivered; 82 delivered direct, rest assembled in Iran; Iranian designation possibly BMT-2'
                if line[0:3] == r'{\b' or line[0:7] == r"\par{\b":
                    if line[0:3] == '{\\b':
                        supplier = line.split('}\\par')[0].split('{\\b ')[1]
                        recipients = line.split('}\\par{\\b R:} ')[1].split('{\\b     } ')
                    else:
                        recipients = line.split('{\\b     } ')[1:]

                    for recipient in recipients:
                        # Two cases
                        # 1. Recipient contains a country
                        # 2. Recipient contains '\tab\tab' Which means to use the previous country
                        if recipient[0:8] == '\\tab\\tab':
                            # Use the previous country
                            country_data = recipient.split('\\tab\\tab')[1].split('\\tab')
                            pass
                        else:
                            country = recipient.split('\\tab')[0]
                            country_data = recipient.split('\\tab')[1:]
                        row = [supplier, country, country_data[0], country_data[1], country_data[2], country_data[3],
                            country_data[4],
                            country_data[5], country_data[6].split('\\par')[0]]
                        rows.append(
                            [element.strip() for element in row])


        rtf_df = pl.DataFrame(rows, schema=["Supplier", "Recipient", "Ordered", "No. Designation", "Weapon Description",

                                            "Year(s) Weapon of Order", "Year Delivery", "Of Delivered", "No. Comments"], orient="row")
        
        processed_rtf = self.rtf_data_processing(rtf_df)
        processed_rtf.write_csv("./data/processed_rtf.csv")
        print(" wrote processed_rtf")

        return processed_rtf

    def replace_unicode_chars(self, df: pl.DataFrame, col_name: str) -> pl.Series:
        if col_name not in df.columns:
            msg = "column name is invalid"
            raise Exception(msg)
        
        col = df[col_name]
        regex = re.compile(r"\\u(\d+)\?") #look for vals like 123 w ? at the end
        for i, val in enumerate(col):
            match = regex.search(val)
            if match:
                hex_code = val.split("\\u")[1].split("?")[0]
                # Convert the hex code to an integer and then to its corresponding unicode character
                char = chr(int(hex_code))

                # Replace the original value with the new value containing the unicode character
                col[i] = val.replace(match.group(), char)

        return col


    def rtf_data_processing(self, df: pl.DataFrame) -> pl.DataFrame:
        df = df.with_columns([
            pl.when(pl.col('Year(s) Weapon of Order').str.contains(r'\(.*\)'))
            .then(pl.lit("Yes"))
            .otherwise(pl.lit("No"))
            .alias("is estimated year order")
        ])

        df = df.with_columns([
            pl.col('Year(s) Weapon of Order').str.replace_all(r"[()]", "").alias('Year(s) Weapon of Order').cast(pl.Int64)
        ])

        return df


    def joined_table(self, df_rtf: pl.DataFrame, csv_df: pl.DataFrame) -> pl.DataFrame:
        # remove spaces
        csv_df = csv_df.with_columns(csv_df['Designation'].str.strip_chars())

        processed_df = df_rtf.with_columns(self.replace_unicode_chars(df_rtf, "No. Designation"))
        processed_df = processed_df.with_columns(self.replace_unicode_chars(df_rtf, "No. Comments"))

        joined_df = csv_df.join(processed_df,
                            left_on=['Seller', 'Buyer',
                                        'Designation', 'Order date',
                                        ],
                            right_on=["Supplier", "Recipient",
                                        "No. Designation", 'Year(s) Weapon of Order',
                                        ],
                            how="left")
        joined_df = joined_df.select(
            ['Deal ID', 'Seller', 'Buyer', 'Designation', 'Description', 'Armament category', 'Order date',
            'Order date is estimate', 'Numbers delivered', 'Numbers delivered is estimate', 'Delivery year',
            'Delivery year is estimate', 'Status', 'SIPRI estimate', 'TIV deal unit', 'TIV delivery values',
            'Local production', 'No. Comments'])

        joined_df = pl.DataFrame.unique(joined_df) #remove dup rows

        return joined_df
    
    def read_file(self, file_path: str) -> List[str]:
        if not os.path.exists(file_path):
            msg = f"path {file_path} does not exist"
            raise FileNotFoundError(msg)
        
        with open(file_path, 'r') as file:
            result = file.readlines()

        return result

# -----------------------------------------------------------------------------------------------------------------------

def main():
    reader = Reader()
    trade_register_path = './data/Trade-Register-1950-2021.rtf'
    csv_data_path = "./data/data.txt"

    reader.join_trade_registers(trade_register_path, csv_data_path)


if __name__ == "__main__":
    main()
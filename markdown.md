These are the files I have worked on either independently and/or with another member of my teams that related to data engineering, my other responsablities were building the website. I have put all of the relevant files in the "pipeline" folder.

pipeline folder:
    Processed data were used in community_detection.py...

    trades_processor is responsible for getting all the data about trade registers and processing them.

    raw data and processed data are in data folder

    map folder is responsible for creating the borders of all countries from 1950s onwards

    MILEX_PRIO lightly processes the military expenditure and UDCP (armed conflicts dataset) (data were already provided to us in excel format)
        ML: contains some files that were not written by me, but use the processed milex and prio data


    data folder:
        Contains all raw and processed data.


    map folder:
        countries.py:
            We have a list of countries and their borders. This is processing data to later be used in the visualization website for creating the borders visually.
            The script first gets a list of IDs, stores it in newIDSJson.txt (I know it's not JSON, I blame past me, but the format of it is JSON but stored as a text file for some reason).
            That is then used to create a CSV file of borders of a given country from a given start date to an end date... if the end is 9999, then it's until the current year (2022). Running countries.py should give the files... they are not included because GitHub doesn't like it (too large). The JSON file of the newidsjson.txt is in the src/data (the react website).
        
        trades_processor folder:
            ingestion.py:
                This is a comprehensive project. A lot of the scripts written here are one-offs, except the pipeline folder, which was initially designed to call the SIPRI database for new data, to then be used in the trade visualization website we created.
                SIPRI changed their UI and API endpoints as of March 2024, making it much simpler to obtain the data (you can get all relevant data already in CSV format), so there is no need for that pipeline anymore... I included it regardless.
                The website used to be pure HTML, with no option to download data, which meant making POST requests and writing the raw data into a text file.
                There are two databases... one is trade registers or transfer of major weapon deals (1950 - 2021) and another one being the main database looking at the trade data between countries from 1950 - 2022.

            reader.py:
                This was designed to wrangle data, find relative info making data frames, and output local CSV files to be later used for community detection and ML attempts.
                The RTF file (trade registers) contains the number of goods ordered (ordered column), a comments column, and estimated delivery year, which are joined with the trades (data.txt) file... they both share a lot of data under different column names... i.e. (data.Seller == rtf.Supplier... or data.buyer == rtf.Recipient).
                The reader is responsible for processing the trade register RTF file and data.txt outputted by the ingestion.py... create data frames from both, join the relevant trade data into a unified dataframe, and output it as a CSV file.

            converter.py:
                Utility functions for converting some columns to int64 format (columns with year data) and converting the numeric CSV to JSON.

        MILEX_PRIO:
            This file contains processing and plots that I wrote.
            They load the SIPRI military expenditure and UCDP-PRIO data to get some plot data, some were used, some were not.
        
            ML:
                I helped with this file... but it is not mainly my work... data processing was used here.

            processing.py:
                Reads the Excel sheets, does some processing (dropping irrelevant columns, null points, etc.). Pandas was used here.

            plot.py:
                Creates xs and ys, plots them, and saves them.
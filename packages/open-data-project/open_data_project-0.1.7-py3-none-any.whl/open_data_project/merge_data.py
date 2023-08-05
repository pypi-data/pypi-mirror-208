### Setting the environment
import pandas as pd
import os
import datetime as dt
import regex as re
import json

def load_ckan_data(folder_ckan):
    ckan_source = pd.DataFrame()

    if os.listdir(folder_ckan):
        for dirname, _, filenames in os.walk(folder_ckan):
            for filename in filenames:
                if filename.rsplit(".", 1)[1] == "csv":
                    ckan_source = pd.concat(
                        [
                            ckan_source,
                            pd.read_csv(
                                folder_ckan + r"/" + filename, parse_dates=["DateCreated","DateUpdated"], lineterminator='\n'
                            ),
                        ]
                    )
        ckan_source["Source"] = "ckan API"

    return ckan_source


def load_scotgov_data(folder_scotgov):
    ### From scotgov csv
    filedir = f"{folder_scotgov}/scotgov-datasets-sparkql.csv"
    if os.path.exists(filedir):
        scotgov_source = pd.read_csv(filedir)
        scotgov_source = scotgov_source.rename(
            columns={
                "title": "Title",
                "category": "OriginalTags",
                "organization": "Owner",
                "notes": "Description",
                "date_created": "DateCreated",
                "date_updated": "DateUpdated",
                "url": "PageURL",
                "licence":"License"
            }
        )
        scotgov_source["Source"] = "sparql"

        try:
            scotgov_source['DateUpdated'] = pd.to_datetime(scotgov_source['DateUpdated'], utc=True).dt.tz_localize(None)
        except:
            try:
                scotgov_source['DateUpdated'] = pd.to_datetime(scotgov_source['DateUpdated'], utc=True, format="ISO8601").dt.tz_localize(None)
            except:
                # If we get to this stage, give up and just blank the date
                print("WARNING: Failed to parse date - " + scotgov_source['DateUpdated'])
                scotgov_source['DateUpdated'] = None
        try:
            scotgov_source['DateCreated'] = pd.to_datetime(scotgov_source['DateCreated'], utc=True).dt.tz_localize(None)
        except:
            try:
                scotgov_source['DateCreated'] = pd.to_datetime(scotgov_source['DateCreated'], utc=True, format="ISO8601").dt.tz_localize(None)
            except:
                # If we get to this stage, give up and just blank the date
                print("WARNING: Failed to parse date - " + scotgov_source['DateCreated'])
                scotgov_source['DateCreated'] = None
    else:
        scotgov_source = pd.DataFrame()

    return scotgov_source


def load_arcgis_data(folder_arcgis):
    arcgis_source = pd.DataFrame()
    
    if os.listdir(folder_arcgis):
        for dirname, _, filenames in os.walk(folder_arcgis):
            for filename in filenames:
                if filename.rsplit(".", 1)[1] == "csv":
                    arcgis_source = pd.concat(
                        [
                            arcgis_source,
                            pd.read_csv(
                                folder_arcgis + r"/" + filename, parse_dates=["DateCreated","DateUpdated"]
                            ),
                        ]
                    )
        arcgis_source["Source"] = "arcgis API"

    return arcgis_source


def load_usmart_data(folder_usmart):
    usmart_source = pd.DataFrame()
    
    if os.listdir(folder_usmart):
        for dirname, _, filenames in os.walk(folder_usmart):
            for filename in filenames:
                if filename.rsplit(".", 1)[1] == "csv":
                    usmart_source = pd.concat(
                        [
                            usmart_source,
                            pd.read_csv(
                                folder_usmart + r"/" + filename, parse_dates=["DateCreated","DateUpdated"]
                            ),
                        ]
                    )
        usmart_source["Source"] = "USMART API"
        usmart_source["DateUpdated"] = usmart_source["DateUpdated"].dt.tz_localize(None)
        usmart_source["DateCreated"] = usmart_source["DateCreated"].dt.tz_localize(None)

    return usmart_source


def load_dcat_data(folder_dcat):
    dcat_source = pd.DataFrame()

    if os.listdir(folder_dcat):
        for dirname, _, filenames in os.walk(folder_dcat):
            for filename in filenames:
                if filename.rsplit(".", 1)[1] == "csv":
                    dcat_source = pd.concat(
                        [
                            dcat_source,
                            pd.read_csv(
                                folder_dcat + r"/" + filename, parse_dates=["DateCreated","DateUpdated"]
                            ),
                        ]
                    )
        dcat_source["DateUpdated"] =  dcat_source["DateUpdated"].dt.tz_localize(None)
        #source_dcat["DateCreated"] = source_dcat["DateCreated"].dt.tz_localize(None) ### DateCreated currently not picked up in dcat so all are NULL
        dcat_source["Source"] = "DCAT feed"

    return dcat_source


def load_web_scraped_data(web_scraped_folder):
    scraped_data = pd.DataFrame()
    
    if os.listdir(web_scraped_folder):
        for dirname, _, filenames in os.walk(web_scraped_folder):
            for filename in filenames:
                if filename.rsplit(".", 1)[1] == "csv":
                    scraped_data = pd.concat(
                        [
                            scraped_data,
                            pd.read_csv(
                                web_scraped_folder + r"/" + filename, parse_dates=["DateCreated","DateUpdated"]
                            ),
                        ]
                    )
        scraped_data["Source"] = "Web Scraped"

    return scraped_data

empty_df = pd.DataFrame()
def merge_data(ckan_source=empty_df, dcat_source=empty_df, scotgov_source=empty_df, arcgis_source=empty_df, usmart_source=empty_df, web_scrapers_source=empty_df,output_fold=""):

    ### Combine all data into single table
    concat_list=[]
    source_list = [ckan_source, dcat_source, arcgis_source, usmart_source, scotgov_source, web_scrapers_source]
    for src in source_list:
        if not src.empty:
            concat_list.append(src)  
    data = pd.concat(
        #maybe concatlist
      source_list
    )
    data = data.reset_index(drop=True)

    ### Saves copy of data without cleaning - for analysis purposes
    data.to_json(f"{output_fold}/merged_output_untidy.json", orient="records", date_format="iso")

    ### clean data
    data = clean_data(data)
    

    ### Output cleaned data to json
    data.to_json(f"{output_fold}/merged_output.json", orient="records", date_format="iso")

    return data


def clean_data(dataframe):
    """cleans data in a dataframe
    Args:
        dataframe (pd.dataframe): the name of the dataframe of data to clean
    Returns:
        dataframe: dataframe of cleaned data
    """
    ### to avoid confusion and avoid re-naming everything...
    data = dataframe
    ### Format dates as datetime type
    data["DateCreated"] = pd.to_datetime(
        data["DateCreated"], format="%Y-%m-%d", errors="coerce", utc=True
    ).dt.date
    data["DateUpdated"] = pd.to_datetime(
        data["DateUpdated"], format="%Y-%m-%d", errors="coerce", utc=True
    ).dt.date
    ### Inconsistencies in casing for FileType
    data["FileType"] = data["FileType"].str.upper()
    ### Creating a dummy column
    data["AssetStatus"] = None

    ### Cleaning dataset categories
    def tidy_categories(categories_string):
        """tidies the categories: removes commas, strips whitespace, converts all to lower and strips any trailing ";"
        Args:
            categories_string (string): the dataset categories as a string
        """
        tidied_string = str(categories_string).replace(",", ";")
        tidied_list = [
            cat.lower().strip() for cat in tidied_string.split(";") if cat != ""
        ]
        tidied_string = ";".join(str(cat) for cat in tidied_list if str(cat) != "nan")
        if len(tidied_string) > 0:
            if tidied_string[-1] == ";":
                tidied_string = tidied_string[:-1]
        return tidied_string

    ### Tidy tag columns
    data["OriginalTags"] = data["OriginalTags"].apply(tidy_categories)
    data["ManualTags"] = data["ManualTags"].apply(tidy_categories)

    ### Creating dataset categories for ODS
    def find_keyword(str_tofind, str_findin):
        """Finds if single word or phrase exists in string
        Args:
            str_tofind (str): the word or phrase to find
            str_findin (str): the body of text to search in
        Returns:
            boolean: True if match is found
        """
        if re.search(r"\b" + re.escape(str_tofind) + r"\b", str_findin, re.I):
            return True
        return False

    def match_categories(str_tocategorise):
        """Cycles through keywords and keyphrases to check if used in body of text
        Args:
            str_tocategorise (str): body of text to search in
        Returns:
            list: the resulting categories as a string, as well as a dictionary of the keyphrases which resulted in a category
        """
        category_dict = {}
        for category in odp_categories.keys():
            keyword_list = []
            for keyword in odp_categories[category]:
                if find_keyword(keyword, str_tocategorise):
                    keyword_list.append(keyword)
                    category_dict[category] = keyword_list
        if len(category_dict) == 0:
            category_list = "Uncategorised"
        else:
            category_list = ";".join(list(category_dict.keys()))
        return [category_list, category_dict]

    def get_categories(row_index):
        """combines title and description together to then search for keyword or keyphrase in
        Args:
            row_index (pandas df row): a single row in a pandas dataframe to check. Must have columns "Title" and "Description"
        Returns:
            list: the resulting categories as a string, as well as a dictionary of the keyphrases which resulted in a category
        """
        str_title_description = (
            str(row_index["Title"]) + " " + str(row_index["Description"])
        )
        categories_result = match_categories(str_title_description)
        return categories_result

    with open("ODPCategories.json") as json_file:
        odp_categories = json.load(json_file)

    ### Apply ODS categorisation
    data[["ODPCategories", "ODPCategories_Keywords"]] = data.apply(
        lambda x: get_categories(x), result_type="expand", axis=1
    )

    ### Tidy licence names
    def tidy_licence(licence_name):
        """Temporary licence conversion to match export2jkan -- FOR ANALYTICS ONLY, will discard in 2022Q2 Milestone
        Returns:
            string: a tidied licence name
        """
        known_licences = {
            "https://creativecommons.org/licenses/by-sa/3.0/": "Creative Commons Attribution Share-Alike 3.0",
            "https://creativecommons.org/licenses/by/4.0/legalcode": "Creative Commons Attribution 4.0 International",
            "https://creativecommons.org/licenses/by/4.0": "Creative Commons Attribution 4.0 International",
            "http://creativecommons.org/licenses/by-sa/3.0/": "Creative Commons Attribution Share-Alike 3.0",
            "http://creativecommons.org/licenses/by/4.0/legalcode": "Creative Commons Attribution 4.0 International",
            "http://creativecommons.org/licenses/by/4.0": "Creative Commons Attribution 4.0 International",
            "Creative Commons Attribution 4.0": "Creative Commons Attribution 4.0 International",
            "https://creativecommons.org/share-your-work/public-domain/cc0": "Creative Commons CC0",
            "https://rightsstatements.org/page/NoC-NC/1.0/": "Non-Commercial Use Only",
            "https://opendatacommons.org/licenses/odbl/1-0/": "Open Data Commons Open Database License 1.0",
            "http://creativecommons.org/share-your-work/public-domain/cc0": "Creative Commons CC0",
            "http://rightsstatements.org/page/NoC-NC/1.0/": "Non-Commercial Use Only",
            "http://opendatacommons.org/licenses/odbl/1-0/": "Open Data Commons Open Database License 1.0",
            "Open Data Commons Open Database License 1.0": "Open Data Commons Open Database License 1.0",
            "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/": "Open Government Licence v2.0",
            "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/": "Open Government Licence v3.0",
            "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/": "Open Government Licence v2.0",
            "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/": "Open Government Licence v3.0",
            "Open Government Licence 3.0 (United Kingdom)": "Open Government Licence v3.0",
            "UK Open Government Licence (OGL)": "Open Government Licence v3.0",
            "Open Government": "Open Government Licence v3.0",
            "uk-ogl": "Open Government Licence v3.0",
            "OGL3": "Open Government Licence v3.0",
            "https://rightsstatements.org/vocab/NKC/1.0/": "No Known Copyright",
            "https://creativecommons.org/publicdomain/mark/1.0/": "Public Domain",
            "http://rightsstatements.org/vocab/NKC/1.0/": "No Known Copyright",
            "http://creativecommons.org/publicdomain/mark/1.0/": "Public Domain",
            "Other (Public Domain)": "Public Domain",
            "Public Domain": "Public Domain",
            "Public Sector End User Licence (Scotland)": "Public Sector End User Licence (Scotland)",
        }

        for key in known_licences.keys():
            if str(licence_name).lower().strip(" /") == key.lower().strip(" /"):
                return known_licences[key]

        if str(licence_name) == "nan":
            tidied_licence = "No licence"
        else:
            tidied_licence = "Custom licence: " + str(licence_name)
        return tidied_licence

    data["License"] = data["License"].apply(tidy_licence)


    def tidy_file_type(file_type):
        """ Temporary data type conversion
        Args:
            file_type (str): the data type name
        Returns:
            tidied_file_type (str): a tidied data type name
        """
        file_types_to_tidy = {
            "application/x-7z-compressed": "7-Zip compressed file",
            "ArcGIS GeoServices REST API": "ARCGIS GEOSERVICE",
            "Esri REST": "ARCGIS GEOSERVICE",
            "Atom Feed": "ATOM FEED",
            "htm": "HTML",
            "ics": "iCalendar",
            "jpeg": "Image",
            "vnd.openxmlformats-officedocument.spreadsheetml.sheet": "MS EXCEL",
            "vnd.ms-excel": "MS EXCEL",
            "xls": "MS EXCEL",
            "xlsx": "MS EXCEL",
            "doc": "MS Word",
            "docx": "MS Word",
            "QGIS": "QGIS Shapefile",
            "text": "TXT",
            "web": "URL",
            "UK/DATA/#TABGB1900": "URL",
            "UK/ROY/GAZETTEER/#DOWNLOAD": "URL",
            "Web Mapping Application": "WEB MAP",
            "mets": "XML",
            "alto": "XML",
        }
        tidied_data_type = "NULL"

        for key in file_types_to_tidy.keys():
            if str(file_type).lower().strip(". /") == key.lower().strip(". /"):
                tidied_file_type = file_types_to_tidy[key]
                return tidied_file_type

        if (
            str(file_type) == "nan"
            or str(file_type) == ""
        ):
            tidied_file_type = "No file type"
        else:
            # print("file type: ", file_type)
            tidied_file_type = str(file_type).strip(". /").upper()

        return tidied_file_type

    ### Inconsistencies in casing for FileType
    data['FileType'] = data['FileType'].apply(tidy_file_type)

    return data


if __name__ == "__main__":

    source_ckan = load_ckan_data("data/ckan/")

    ### From scotgov csv
    source_scotgov = load_scotgov_data("data/sparkql/")

    ### From arcgis api
    source_arcgis = load_arcgis_data("data/arcgis/")
    
    ### From usmart api
    source_usmart = load_usmart_data("data/USMART/")

    ## From DCAT
    source_dcat = load_dcat_data("data/dcat/")

    merge_data(ckan_source=source_ckan, dcat_source= source_dcat, usmart_source=source_usmart, arcgis_source=source_arcgis, scotgov_source=source_scotgov, output_fold = "data")
    
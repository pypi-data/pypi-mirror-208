# Packages: beautifulsoup4, csv, requests
import requests
import csv
from bs4 import BeautifulSoup

# Global Variables
ODR_URL = "https://www.sqa.org.uk/sqa/57523.html"


def get_headers():
    """
    Gets headers to make a request from the URL. Optimized so website doesn't think a bot is making a request.

    Args:
        NULL

    Returns:
        headers (Dictionary) : header values
    """
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "3600",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
    }
    return headers


def csv_output(header, data):
    """
    Create output csv file of the final data scrapped from website.

    Args:
        header (List): A list of header items that are Strings.
        data (List): A list of records.
    Returns:
        NULL
    """

    with open("../data/scraped-results/output_sqa.csv", "w", encoding="UTF8") as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write the data
        for record in data:
            writer.writerow(record)


def fetch_available_years():
    """
    Fetches links to pages of available years from ODR_URL. It uses the dropdown menu on the 'Data' button.

    Returns:
        list_of_links (List): A list of URLs linking to the pages for each data category.
    """
    dict_of_links = {}
    initial_req = requests.get(ODR_URL, get_headers())
    initial_soup = BeautifulSoup(initial_req.text, "html.parser")
    data_button = initial_soup.find("select", id="selYear")
    dropdown_list = data_button.find_all("option")

    for dropdown_item in dropdown_list:
        dict_of_links[dropdown_item.contents[0]] = "https://www.sqa.org.uk/sqa/" + dropdown_item["value"]
    keys_to_skip = ["--- Select Year ---", "Statistics archive", "Related", "Derived Grades 2003"]
    [dict_of_links.pop(d) for d in keys_to_skip]

    return dict_of_links


def fetch_year_page(link: str) -> BeautifulSoup:
    """
    Fetches the content of pages of available years.

    Returns:
        BeautifulSoup object of the pages.
    """
    req = requests.get(link, get_headers())
    return BeautifulSoup(req.content, "html.parser")


def fetch_datasets(page: BeautifulSoup) -> list:
    """
    Fetches the datasets present on a page.

    Returns:
        list_of_lists_of_datasets (List): A list of datasets present on the specific page.
    """
    list_of_lists_of_datasets = []
    content = page.find(id="content")
    unsorted_lists = content.find_all("ul")
    for unsorted_list in unsorted_lists:
        list_of_datasets = unsorted_list.find_all("a")
        list_of_lists_of_datasets.append(list_of_datasets)

    return list_of_lists_of_datasets


def create_title(part1: str) -> str:
    """
    Adds 'SQA' at the beginning of the input to create the title of the dataset

    Returns:
        stripped_title (str): A string of dataset's title.
    """

    return 'SQA ' + part1


def fetch_asset_url(page: BeautifulSoup) -> str:
    """
    Fetches the asset url of the dataset from the BeautifulSoup object.

    Returns:
        url (str): A string of dataset's asset url.
    """
    link = page.get("href")
    if link.startswith("//"):
        url = "https:" + link
    elif link.startswith("files"):
        url = "https://www.sqa.org.uk/sqa/" + link
    elif link.startswith("/sqa"):
        url = "https://www.sqa.org.uk" + link
    else:
        url = link

    return url


def fetch_create_date(page: BeautifulSoup, ul: BeautifulSoup) -> tuple:
    """
    Fetches the create date and the date of correction of the dataset from the BeautifulSoup object.

    Returns:
        date (str): A string of dataset's create date.
    """

    fetched_create_date = "NULL"
    fetched_update_date = "NULL"

    part = page.find("a", string=ul.get_text())
    find_ul = part.find_parent("ul")
    find_siblings = find_ul.next_siblings
    for sibling in find_siblings:
        if "<h2>" in repr(sibling):
            return fetched_create_date, fetched_update_date
        elif "Date of publication" in repr(sibling):
            fetched_create_date = sibling.get_text().split(":")[1].strip(" .\xa0&nbsp")
        elif "Date of correction" in repr(sibling):
            fetched_update_date = sibling.get_text().split(":")[1].strip(" .\xa0&nbsp")

    return fetched_create_date, fetched_update_date


def fetch_file_size(page: BeautifulSoup, ul: BeautifulSoup) -> tuple:
    size = "NULL"
    unit = "NULL"
    part = page.find("a", string=ul.get_text())
    size_list = part.find_parent("li").contents
    for item in size_list:
        if "(" in item:
            size = item.strip(" \xa0&nbsp()\n").split(" ")[0]
            unit = item.strip(" \xa0&nbsp()\n").split(" ")[1]

    return size, unit


def fetch_description(ds, ys):
    descr = "A range of statistical reports for SQA qualifications for " + ys.split(" ", 1)[1] + "."

    return descr


def create_filename(part2: BeautifulSoup) -> str:
    """
    Extracts the title of the dataset from the input
    Returns:
        A string of dataset's title.
    """

    return part2.get_text()


if __name__ == "__main__":
    # Record Headings
    header = [
        "Title",
        "Owner",
        "PageURL",
        "AssetURL",
        "FileName",
        "DateCreated",
        "DateUpdated",
        "FileSize",
        "FileSizeUnit",
        "FileType",
        "NumRecords",
        "OriginalTags",
        "ManualTags",
        "License",
        "Description",
    ]
    data = []

    print("Getting available years")
    category_links = fetch_available_years()
    for year_string in category_links.keys():
        print("Getting", year_string)
        years_page = fetch_year_page(category_links[year_string])
        owner = "Scottish Qualifications Authority (SQA)"
        title = create_title(year_string)
        # print("title", title)
        description = fetch_description(years_page, year_string)
        pageurl = category_links[year_string]
        list_datasets = fetch_datasets(years_page)
        for list in list_datasets[:-3]:
            # print("list", list)
            for dataset in list:
                # print("dataset", dataset)
                asset_url = fetch_asset_url(dataset)
                file_name = create_filename(dataset)
                create_date, update_date = fetch_create_date(years_page, dataset)
                file_sizeandunit = fetch_file_size(years_page, dataset)
                file_size = file_sizeandunit[0]
                file_unit = file_sizeandunit[1]
                data_type = dataset.get("href").split(".")[-1]
                num_recs = "NULL"
                sqa_licence = "unknown" # contact SQA regarding license

                output = [
                    title,
                    owner,
                    pageurl,
                    asset_url,
                    file_name,
                    create_date,
                    update_date,
                    file_size,
                    file_unit,
                    data_type,
                    num_recs,
                    "NULL",
                    "NULL",
                    sqa_licence,
                    description,
                ]
                data.append(output)

    print("Outputting to CSV")
    csv_output(header, data)


"""
issues with this scraper:
- year before 2000 don't return a dataset, even though there are unordered lists present"
- in many (all?) years, the last datasets seem to be missing
"""


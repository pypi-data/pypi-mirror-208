import pandas as pd
from dataclasses import dataclass
from typing import List
from math import isnan
import markdown
import re
import yaml
import shutil
import os
import urllib


@dataclass
class DataFile:
    url: str
    size: float
    size_unit: str
    file_type: str
    file_name: str
    show_name: str


@dataclass
class Dataset:
    title: str
    owner: str
    page_url: str
    date_created: str
    date_updated: str
    odp_categories: List[str]
    license: str
    description: str
    num_records: int
    files: List[DataFile]


### Extraction of date from ISO datetime ISO.
def strip_date_from_iso8601(df_name, col_list):
    for col in col_list:
        df_name[col] = df_name[col].str.split("T").str[0]
    return


def ind(name):
    f = [
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
        "Source",
        "AssetStatus",
        "ODPCategories",
        "ODPCategories_Keywords"
    ]
    return f.index(name)


def splittags(tags):
    if type(tags) == str:
        if tags == "":
            return []
        return tags.split(";")
    else:
        return []


def makeint(val):
    try:
        return int(val)
    except:
        pass
    try:
        return int(float(val))
    except:
        pass
    return None

def organize_data(fulld):
    data = {}
    for record in fulld.values:
        record_id = str(record[ind("PageURL")]) + record[ind("Title")]
        if record_id not in data:
            ds = Dataset(
                title=record[ind("Title")],
                owner=record[ind("Owner")],
                page_url=record[ind("PageURL")],
                date_created=record[ind("DateCreated")],
                date_updated=record[ind("DateUpdated")],
                odp_categories=splittags(record[ind("ODPCategories")]),
                license=record[ind("License")],
                description=str(record[ind("Description")]),
                num_records=makeint(record[ind("NumRecords")]),
                files=[],
            )
            # Sort categories to keep consistent when syncing
            ds.odp_categories.sort()
            data[record_id] = ds

        data[record_id].files.append(
            DataFile(
                url=record[ind("AssetURL")],
                size=record[ind("FileSize")],
                size_unit=record[ind("FileSizeUnit")],
                file_type=record[ind("FileType")],
                file_name=record[ind("FileName")],
                show_name=record[ind("FileName")] if record[ind("FileName")] else record[ind("FileType")],
            )
        )
    return data


unknown_licences = []


def license_link(l):

    known_licence_links = {
        "Open Government Licence v2.0": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/",
        "Open Government Licence v3.0": "https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
        "Creative Commons Attribution Share-Alike 3.0": "https://creativecommons.org/licenses/by-sa/3.0/",
        "Creative Commons Attribution Share-Alike 4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
        "Creative Commons Attribution 4.0 International": "https://creativecommons.org/licenses/by/4.0/",
        "Open Data Commons Open Database License 1.0": "https://opendatacommons.org/licenses/odbl/",
        "Creative Commons CC0": "https://creativecommons.org/share-your-work/public-domain/cc0",
        "Non-Commercial Use Only": "https://rightsstatements.org/page/NoC-NC/1.0/",
        "No Known Copyright": "https://rightsstatements.org/vocab/NKC/1.0/",
        "Public Domain": "https://creativecommons.org/publicdomain/mark/1.0/",
    }

    for key in known_licence_links.keys():
        if l == key:
            return known_licence_links[key]

    if l not in unknown_licences:
        unknown_licences.append(l)
        # print("Unknown license: ", l)
    return l

def replace_folder(datasets_folder):
    ### Replace folder by deleting and writing   
    if os.path.exists(datasets_folder):
        shutil.rmtree(datasets_folder)
    os.makedirs(datasets_folder)

def prepare_and_export_data(full_d, datasets_folder):
    strip_date_from_iso8601(full_d, ["DateCreated", "DateUpdated"])
    organized_data = organize_data(full_d)
    replace_folder(datasets_folder)

    for n, (k, ds) in enumerate(organized_data.items()):
        y = {"schema": "default"}
        y["title"] = ds.title
        y["organization"] = ds.owner
        
        if ds.description != "{{description}}":
            y["notes"] = markdown.markdown(ds.description)
        else:
            y["notes"] = markdown.markdown("")

        y["original_dataset_link"] = ds.page_url
        y["resources"] = [
            {"name": d.show_name, "url": d.url, "format": d.file_type}
            for d in ds.files
            if d.url
        ]
        y["license"] = license_link(ds.license)
        y["category"] = ds.odp_categories
        y["maintainer"] = ds.owner
        y["date_created"] = ds.date_created
        y["date_updated"] = ds.date_updated
        y["records"] = ds.num_records
        # fn = f'{ds.owner}-{ds.title}'
        # fn = re.sub(r'[^\w\s-]', '', fn).strip()[:100]
        fn = urllib.parse.quote_plus(f"{(ds.owner).lower()}-{(ds.title).lower()}")
        # fn = f"{ds.owner}-{ds.title}"
        # ^^ need something better for filenames...
        with open(f"{datasets_folder}/{fn}.md", "w") as f:
            f.write("---\n")
            f.write(yaml.dump(y))
            f.write("---\n")


if __name__ == "__main__":
    full_data = pd.read_json("data/merged_output.json", orient="records").fillna("")
    prepare_and_export_data(full_data, "../jkan/_datasets/")

"""Generates new Mock and Expected Test data based on current code
to run navigate to root directory and run `python -m tests.generate_new_mock_data`
"""
from urllib import request
import csv
import json
import os
from os.path import isfile, join
import sys
import shutil
file_dir = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(file_dir)
sys.path.append(parent)
from usmart import ProcessorUSMART
from dcat import ProcessorDCAT
from arcgis import ProcessorARCGIS
from ckan import ProcessorCKAN
from merge_data import *
from export2jkan import * 

def list_sources(dir):
    sources_path = os.path.abspath(dir)
    sources = [
        f.split(".")[0]
        for f in os.listdir(sources_path)
        if isfile(join(sources_path, f))
    ]
    return sources

def get_urls():
    urls_list = {}
    with open("sources.csv", "r", encoding="utf-8") as file:
        csv_file = csv.DictReader(file)
        for row in csv_file:
            urls_list[row["Name"]] = {
                "url": row["Source URL"],
                "type": row["Processor"],
            }
    return urls_list


def get_json(url):
    req = request.Request(url)
    return json.loads(request.urlopen(req).read().decode())

def clean_folder(folder):
    urls = get_urls()
    if os.path.exists(folder):    
        for file in os.listdir(folder):
            if isfile(join(folder, file)):
                filename = file.split(".")[0]
                if filename not in urls.keys():
                    os.remove(join(folder,file))


def save_json(data, location):
    with open(location, "w+", newline="", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    

def test_get_datasets(name, type):
    match (type):
        case "USMART":
            test_proc = ProcessorUSMART()
        case "dcat":
            test_proc = ProcessorDCAT()
        case "arcgis":
            test_proc = ProcessorARCGIS()
        case "ckan":
            # no python parser implemented
            test_proc = ProcessorCKAN()
            
    owner = "test_owner"
    outputdir = os.path.join("tests", "mock_data", type, "expected")
    if os.path.exists(outputdir):
        clean_folder(outputdir)
    else:
        os.makedirs(outputdir)  
    
    if type == "ckan":
        urls = get_urls()
        start_url = urls[name]["url"]        
        
    else: 
        start_url = "file:///" + os.path.abspath(
        "tests/mock_data/" + type + "/" + name + ".json")
  
    fname = os.path.join(outputdir, name + ".csv")
    if os.path.exists(fname):
        os.remove(fname)

    test_proc.get_datasets(owner, start_url, fname)


def test_merge_data():
    output_dir = os.path.join("tests", "mock_data", "merge_data", "expected")
    ckan = load_ckan_data("tests/mock_data/ckan/expected/")
    dcat = load_dcat_data("tests/mock_data/dcat/expected/")
    arcgis = load_arcgis_data("tests/mock_data/arcgis/expected/")
    usmart = load_usmart_data("tests/mock_data/USMART/expected/")
    folder_output = "tests/mock_data/merge_data/expected/"
    
    replace_folder(output_dir)

    merge_data(ckan_source=ckan, dcat_source=dcat, arcgis_source=arcgis, usmart_source= usmart, output_fold=folder_output)


def test_export2jkan():
    outputdir = os.path.join("tests", "mock_data", "export2jkan", "expected")
    f_data = pd.read_json("tests/mock_data/merge_data/expected/merged_output.json", orient = "records").fillna("")
    prepare_and_export_data(f_data, outputdir)    
    

def main():
    url_list = get_urls()
    supported_scrapers = ["USMART", "dcat", "arcgis", "ckan"]

    for name in url_list:
        type_source = url_list[name]["type"]

        print(f"-> {name} | {type_source} | {url_list[name]['url']}")
        if type_source in supported_scrapers:            
            if not os.path.exists(f"tests/mock_data/{type_source}"):
                os.makedirs(f"tests/mock_data/{type_source}")
            
            clean_folder(f"tests/mock_data/{type_source}")

            location = os.path.join("tests", "mock_data", type_source, name + ".json")
            if os.path.exists(location):
                os.remove(os.path.abspath(location))

            if type_source != "ckan":
                json_data = get_json(url_list[name]["url"])
                if type_source == "arcgis":
                    if "next" in json_data["meta"] and json_data["meta"]["next"]:
                        del json_data["meta"]["next"]  # avoids link list urls
                save_json(json_data, location)
                test_get_datasets(name, type_source)
            else:        
                test_get_datasets(name, type_source)
    test_merge_data()
    test_export2jkan()
                                


if __name__ == "__main__":
    '''
    user_response = (False, True)[
        input(
            "This will replace all test data, are you sure you want to continue? Y/n\n"
        )
        == "Y"
    ]
    if user_response:
    '''
    main()

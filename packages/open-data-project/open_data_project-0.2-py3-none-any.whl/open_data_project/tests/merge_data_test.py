import filecmp
import os
from os.path import isfile, join
import csv
import pytest
import pandas as pd
from .. merge_data import *
from .conftest import csv_checker 


def list_sources(dir):
    sources_path = os.path.abspath(dir)
    sources = [
        f.split(".")[0]
        for f in os.listdir(sources_path)
        if isfile(join(sources_path, f))
    ]
    return sources


@pytest.mark.parametrize("sources", list_sources("tests/mock_data/merge_data/expected"))
def test_merge_data(sources):
    ckan = load_ckan_data("tests/mock_data/ckan/expected/")
    dcat = load_dcat_data("tests/mock_data/dcat/expected/")
    arcgis = load_arcgis_data("tests/mock_data/arcgis/expected/")
    usmart = load_usmart_data("tests/mock_data/USMART/expected/")
    outputdir = "tests/mock_data/output/merge_data"
    
    test_f_name = outputdir + "/" + sources + ".json"
    expected_f_name = "tests/mock_data/merge_data/expected/" + sources + ".json"

    if os.path.exists(test_f_name):
        os.remove(test_f_name)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    merge_data(ckan_source=ckan, dcat_source=dcat, arcgis_source=arcgis, usmart_source=usmart, output_fold = outputdir)
    
    csv_filedir = f"{outputdir}/{sources}.csv"
    df = pd.read_json(test_f_name)
    df.to_csv(csv_filedir, index=None)

    with open(csv_filedir, "r", newline="", encoding="utf-8") as check_file:
        csv_check_file = csv.reader(check_file)
        assert csv_checker(csv_check_file)
    os.remove(csv_filedir)
    assert filecmp.cmp(test_f_name, expected_f_name)

import filecmp
import os
from os.path import isfile, join
import csv
import pytest
from .conftest import csv_checker
from ..ckan import ProcessorCKAN
from .generate_new_mock_data import get_urls

test_proc = ProcessorCKAN()

def list_sources(dir):
    
    sources_path = os.path.abspath(dir)
    url_list = get_urls()
    sources = []
    for f in os.listdir(sources_path):
            if isfile(join(sources_path, f)):
                f = f.split(".")[0]
                for name in url_list:                
                    if url_list[name]["type"] == "ckan" and name == f:                    
                        ckan = url_list[name]["url"]
                        sources.append((f, ckan))
                        break        

    return sources

@pytest.mark.parametrize("sources, link_json", list_sources("tests/mock_data/ckan/expected"))
def test_get_datasets(sources, link_json):
    owner = "test_owner"
    outputdir = "tests/mock_data/output/ckan/"
    start_url = link_json
    fname = outputdir + sources + ".csv"
    expected_fname = "tests/mock_data/ckan/expected/" + sources + ".csv"
    if os.path.exists(fname):
        os.remove(fname)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    test_proc.get_datasets(owner, start_url, fname)
    with open(fname, "r", newline="", encoding="utf-8") as check_file:
        csv_check_file = csv.reader(check_file)
        assert csv_checker(csv_check_file)
    assert filecmp.cmp(fname, expected_fname)

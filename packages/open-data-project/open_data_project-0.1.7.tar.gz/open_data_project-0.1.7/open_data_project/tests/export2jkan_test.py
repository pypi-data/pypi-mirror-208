import filecmp
import os
from os.path import isfile, join
import csv
import pytest
import pandas as pd
from .. export2jkan import *



def test_export2jkan():
    full_data = pd.read_json("tests/mock_data/merge_data/expected/merged_output.json", orient="records").fillna("")
    outputdir = "tests/mock_data/output/export2jkan/"

    prepare_and_export_data(full_data, outputdir)

    path = os.path.abspath("tests/mock_data/export2jkan/expected")

    for filename in os.listdir(path):
        if isfile(join(path, filename)):
            test_f_name = outputdir + filename
            expected_f_name = "tests/mock_data/export2jkan/expected/" + filename
            assert filecmp.cmp(test_f_name, expected_f_name)

    
    

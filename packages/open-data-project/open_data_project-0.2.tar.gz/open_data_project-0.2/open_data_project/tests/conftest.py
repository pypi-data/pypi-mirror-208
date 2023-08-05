import validators
import pytest
import dateutil.parser
import ast


def is_valid_string(str_to_check):
    return isinstance(str_to_check, str)


def is_valid_filename(filename_to_check):
    return is_valid_string(filename_to_check)


def is_valid_date(date_to_check):
    if date_to_check:
        try:
            dateutil.parser.isoparse(date_to_check)
        except ValueError:
            return False
    return True


def is_valid_number(str_to_check):
    if str_to_check:
        if '.' in str_to_check:
            str_to_check = str_to_check.split('.', 1)[0]
        return str_to_check.isnumeric()
    return True


def is_valid_file_size_unit(str_to_check):
    file_size_units = [
        "",  # blank
        "bytes",  # alt bytes
        "B",  # Bytes
        "kB",
        "MB",
        "GB",
        "TB",
        "PB",
        "EB",
        "ZB",
        "YB",
        "b",  # bits
        "kb",
        "Mb",
        "Gb",
        "Tb",
        "Pb",
        "Eb",
        "Zb",
        "Yb",
    ]
    return str_to_check in file_size_units


def is_valid_file_type(str_to_check):
    return is_valid_string(str_to_check)

def is_valid_dictionary(str_to_check):
    str_to_check = ast.literal_eval(str_to_check)
    return type(str_to_check) is dict

def is_valid_tags(str_to_check):
    return is_valid_string(str_to_check)


def is_valid_licence(str_to_check):
    licences = {
            "one":"http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/",
            "two":"http://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/",
            "three":"http://opendatacommons.org/licenses/odbl/1-0/",
            "four":"Open Data Commons Open Database License 1.0",
            "five":"uk-ogl",
            "six":"UK Open Government Licence (OGL)",
            "seven":"Open Government Licence 3.0 (United Kingdom)",
            "eight":"OGL3",
            "nine":"https://creativecommons.org/licenses/by/4.0/legalcode",
            "ten":"Creative Commons Attribution 4.0",
            "eleven":"https://creativecommons.org/licenses/by-sa/3.0/",
            "twelve":"",
            "https://creativecommons.org/licenses/by-sa/3.0/": "Creative Commons Attribution Share-Alike 3.0",
            "https://creativecommons.org/licenses/by/4.0/legalcode": "Creative Commons Attribution 4.0 International",
            "https://creativecommons.org/licenses/by/4.0": "Creative Commons Attribution 4.0 International",
            "http://creativecommons.org/licenses/by-sa/3.0/": "Creative Commons Attribution Share-Alike 3.0",
            "http://creativecommons.org/licenses/by/4.0/legalcode": "Creative Commons Attribution 4.0 International",
            "http://creativecommons.org/licenses/by/4.0": "Creative Commons Attribution 4.0 International",
            "Creative Commons Attribution 4.0": "Creative Commons Attribution 4.0 International",
            "https://creativecommons.org/share-your-work/public-domain/cc0": "Creative Commons CC0",
            "no lic":"No licence",
            "other":"Other (Public Domain)",
            "oc":"other-closed",
            "otc":"Custom licence: Other(Not Open)",
            "l":"Other: (Not Open)",
            "custom":"Custom license: other-closed",
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
            "Public Sector End User Licence (Scotland)": "Public Sector End User Licence (Scotland)"
        
    }
    return str_to_check in licences.values()


def is_valid_url(url_to_check):
    if url_to_check:
        if url_to_check[0].isspace():
            url_to_check = url_to_check[1:]
        return validators.url(url_to_check)
    return True


def csv_checker(csv_file):
    result = True
    csv_testers = [
        {"title": "Title", "test_func": is_valid_string},
        {"title": "Owner", "test_func": is_valid_string},
        {"title": "PageURL", "test_func": is_valid_url},
        {"title": "AssetURL", "test_func": is_valid_url},
        {"title": "FileName", "test_func": is_valid_filename},
        {"title": "DateCreated", "test_func": is_valid_date},
        {"title": "DateUpdated", "test_func": is_valid_date},
        {"title": "FileSize", "test_func": is_valid_number},
        {"title": "FileSizeUnit", "test_func": is_valid_file_size_unit},
        {"title": "FileType", "test_func": is_valid_file_type},
        {"title": "NumRecords", "test_func": is_valid_number},
        {"title": "OriginalTags", "test_func": is_valid_tags},
        {"title": "ManualTags", "test_func": is_valid_tags},
        {"title": "License", "test_func": is_valid_licence},
        {"title": "Description", "test_func": is_valid_string},
        {"title": "Source", "test_func": is_valid_string},
        {"title": "ODPCategories", "test_func": is_valid_string},
        {"title": "ODPCategories_Keywords", "test_func": is_valid_dictionary}
    ]
    header_row = 0
    for row_idx, row in enumerate(csv_file):
        if row_idx != header_row:
            for col_idx, cell in enumerate(row):
                assert csv_testers[col_idx]["test_func"](cell)
                # result = False
    return result

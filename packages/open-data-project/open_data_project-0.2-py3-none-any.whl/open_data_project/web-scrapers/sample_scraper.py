from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

def get_all_datasets(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    page = urlopen(req).read()

    soup = BeautifulSoup(page, "html.parser")

    # Add files with their links, last updated and filesize.
    # Check the index here as well
    datasets = []
    files = [a_tag for a_tag in soup.find_all("a", href=True)]
    for anchor in files:
        link = anchor.get("href")
        # include if appropriate
            
        if link.endswith(".kmz") or link.endswith(".csv") or link.endswith(".zip"):
            filename = link.rsplit("/", 1)[-1]
            datasets.append(filename)
                
        
    return datasets

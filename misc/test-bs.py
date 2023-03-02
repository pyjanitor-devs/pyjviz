import ipdb
import sys
from bs4 import BeautifulSoup

with open(sys.argv[1]) as f:
    soup = BeautifulSoup(f, features="xml")

# Find all <b> tags and replace them with <strong> tags
for a_tag in soup.find_all("a"):
    on_click_code = a_tag.attrs.get("xlink:href")
    a_tag.parent.attrs["onclick"] = on_click_code.replace("javascript:", "")
    a_tag.parent.attrs["cursor"] = "pointer"
    del a_tag.attrs["xlink:href"]
    del a_tag.attrs["xlink:title"]

for a_tag in soup.find_all("a"):
    p_tag = a_tag.parent
    for c in a_tag.find_all():
        p_tag.insert(-1, c)
    a_tag.decompose()

# Print the modified HTML output
print(soup.prettify())

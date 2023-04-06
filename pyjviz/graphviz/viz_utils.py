from bs4 import BeautifulSoup

big_strings_table = {}

def replace_a_href_with_onclick(output):
    global big_strings_table
    soup = BeautifulSoup(output, features="xml")

    for a_tag in soup.find_all("a"):
        on_click_code = a_tag.attrs.get("xlink:href")
        on_click_code = on_click_code.replace("javascript:", "")
        # NB: really bad way to do string replacement,
        # quadratic complexity for overall code execution
        for k, v in big_strings_table.items():
            on_click_code = on_click_code.replace(f"%%{k}%%", v)
        a_tag.parent.attrs["onclick"] = on_click_code
        a_tag.parent.attrs["cursor"] = "pointer"
        del a_tag.attrs["xlink:href"]
        del a_tag.attrs["xlink:title"]

    for a_tag in soup.find_all("a"):
        p_tag = a_tag.parent
        for c in a_tag.find_all():
            p_tag.insert(-1, c)
        a_tag.decompose()

    # Print the modified HTML output
    return soup.prettify()

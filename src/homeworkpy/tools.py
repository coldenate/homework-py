"""A surplus of functions that can be used as builtin tools throughout
the library without interfering with the actual classes."""
import json

from bs4 import BeautifulSoup

# due to circular imports, this file may never import homework


def println():
    """A quick little print line function that I loved from c++"""
    print("\n")


def html_to_json(
    content,
    indent=None,
):
    """Convert HTML Tables to json"""
    soup = BeautifulSoup(content, "html.parser")
    rows = soup.find_all("tr")

    headers = {}
    thead = soup.find("thead")
    if thead:
        thead = thead.find_all("th")
        for i in range(len(thead)):
            headers[i] = thead[i].text.strip().lower()
    data = []
    for row in rows:
        cells = row.find_all("td")
        if thead:
            items = {}
            for index in headers:
                items[headers[index]] = cells[index].text
        else:
            items = []
            for index in cells:
                items.append(index.text.strip())
        data.append(items)
    return json.dumps(data, indent=indent)


def cleanup_json(input_data: list, known_classes):
    """This function will attempt to remove any unnecessary data from the rendered
    DOM of a Report Card.
    This targeted data is traditionally created from the use of empty characters.
    returns table_headers if found"""

    # Find the subject
    table_header = None
    subject_found: int = None
    for index, data_object in enumerate(input_data):
        if data_object[0] == "Subject":
            # we canc onclude that this is the false header
            subject_found = index

            table_header = data_object

    #  Locate all the grades
    for index, data_object in enumerate(input_data):
        if index > subject_found:
            # we dont need it to be >= because we want to avoid appending the table key
            if len(data_object[0]) > 4 and len(data_object[0]) < 50:
                known_classes.append(data_object)

    return table_header


def isfloat(num) -> bool:
    """check if the given number is a float type"""  # thanks google!!!
    try:
        float(num)
        return True
    except ValueError:
        return False


def isnumber(num) -> bool:
    """check if a num is a float or an integer"""
    if isinstance(num, float) or isinstance(num, int):
        return True
    if not isinstance(num, float) or not isinstance(num, int):
        return False


def get_index_positions(list_of_elems, element):  # thanks stack overflow!!!
    """Returns the indexes of all occurrences of give element in
    the list- listOfElements"""
    index_pos_list = []
    index_pos = 0
    while True:
        try:
            # Search for item in list from indexPos to the end of list
            index_pos = list_of_elems.index(element, index_pos)
            # Add the index position in list
            index_pos_list.append(index_pos)
            index_pos += 1
        except ValueError:
            break
    return index_pos_list


def cluster(data, maxgap):  # thanks stack overflow!!!
    """Arrange data into groups where successive elements
    differ by no more than *maxgap*

    >>> cluster([1, 6, 9, 100, 102, 105, 109, 134, 139], maxgap=10)
    [[1, 6, 9], [100, 102, 105, 109], [134, 139]]

    >>> cluster([1, 6, 9, 99, 100, 102, 105, 134, 139, 141], maxgap=10)
    [[1, 6, 9], [99, 100, 102, 105], [134, 139, 141]]

    """
    data.sort()
    groups = [[data[0]]]
    for i in data[1:]:
        if abs(i - groups[-1][-1]) <= maxgap:
            groups[-1].append(i)
        else:
            groups.append([i])
    return groups

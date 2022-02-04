"""Get data for repeaters."""

import csv
import requests
from bs4 import BeautifulSoup as Soup
from typing import List
from absl import app
from absl import logging
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_string("data_path", None, "Output location of data file.")

logging.set_verbosity(logging.INFO)


def getStateName(responseText: str) -> str:
    """Parse state name in title field.

    Args:
        responseText: response.text object from requests.

    Returns: State string name.
    """
    soup = Soup(responseText, "html.parser")
    logging.debug("Ingesting soup: %s", soup.prettify())
    if soup.title:
        return soup.title.get_text()
    else:
        return "***No state found."


def writeToFile(content: str, fileout: str) -> None:
    """File output handler.

    Args:
        content: Data to write to file.
        fileout: Path for file location.
    """
    soup = Soup(content, "html.parser")
    with open(fileout, "w") as dataFile:
        dataFile.write(soup.prettify())


def sendRequest(countryCode: str, stateId: int) -> requests.Response:
    """Prepare url and send ping to RepeaterBook.

    Args:
        courntryCode: Two letter country code.
        stateId: Repeater Book's special ID for each state.

    Returns: Response object.
    """
    res: requests.response = None
    try:
        url: str = ("https://www.repeaterbook.com/repeaters/Display_SS.php"
                    + f"?country_code={countryCode.upper()}&state_id={stateId}"
                    + "&loc=%&call=%&use=%")
        res = requests.get(url)
    except Exception as e:
        logging.warning("Could not ping RepeaterBook: %s", e)
    return res


def main(argv) -> None:
    logging.debug("Starting scrape...")
    # COUNTRY_CODE: str = "US"
    # STATE_ID: int = 53
    # BAND_ID: int = 14  # 2 meter
    output: str = ""
    stateIds: dict[str] = []
    frequencies: dict[str] = []

    with open("results/states.tsv", "r") as stateList:
        for row in csv.reader(stateList, delimiter="\t"):
            stateIds.append(row)

    # for stateId, state in stateIds:
    #     logging.info(f"Reading: {stateId} {state}")
    #     response = sendRequest(countryCode="US", stateId=stateId)

    response = sendRequest(countryCode="US", stateId=53)
    soup = Soup(response.text, "html.parser")
    frequencyTable = soup.select(
        'table[class="w3-table sortable w3-responsive w3-striped"]')[0]

    headerElements: List = frequencyTable.select("th")
    frequencyRows: List = frequencyTable.select("tr")
    for row in frequencyRows:
        print("ROW: ", row)
        rowDetails = row.select("td")
        for cell in rowDetails:
            print("    CELL: ", cell.get_text().strip())

    # result = str()
    # writeToFile(result, FLAGS.data_path)


if __name__ == "__main__":
    app.run(main)

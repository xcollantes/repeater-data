"""Get data for repeaters."""

import pandas as pd
import requests
from bs4 import BeautifulSoup as Soup
from typing import List
from absl import app
from absl import logging

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
    stateList: pd.DataFrame = pd.read_csv("data_deps/states.tsv", sep="\t")

    for _, stateRow in stateList.iterrows():
        stateId: str = f"{stateRow['id']:02}"
        stateName: str = stateRow["state"]

        logging.info(f"Reading: {stateId} {stateName}")
        response = sendRequest(countryCode="US", stateId=stateId)
        try:
            soup = Soup(response.text, "html.parser")
            # Repeater title should be "{STATE} Amateur Radio Repeaters"
            if soup.title.text.strip() == "Amateur Radio Repeaters":
                raise Exception(response.url)
        except Exception as e:
            logging.warning("Page not found. Check URL parameters: %s", e)
            continue
        logging.debug("response: %s", soup.prettify())
        logging.info("Processing page for %s", soup.title.text.strip())

        frequencyTable = soup.select(
            'table[class="w3-table sortable w3-responsive w3-striped"]')[0]

        logging.debug("frequencyTable: %s", frequencyTable)

        headerElements: List = frequencyTable.select("th")
        frequencyRows: List = frequencyTable.select("tr")
        with open(f"repeater_data/{stateName.lower().replace(' ' , '_')}.tsv",
                  "w") as repeaterDataFile:

            for cell in headerElements:
                repeaterDataFile.write(cell.get_text().strip() + "\t")

            for row in frequencyRows:
                logging.debug("ROW: ", row)
                rowDetails = row.select("td")
                for cell in rowDetails:
                    cellData: str = cell.get_text().strip()
                    repeaterDataFile.write(cellData + "\t")
                    logging.debug("    CELL: ", cellData)
                repeaterDataFile.write("\n")


if __name__ == "__main__":
    app.run(main)

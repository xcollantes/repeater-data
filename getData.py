"""Get data for repeaters."""

import json
import os
import requests
from bs4 import BeautifulSoup as Soup
from absl import app
from absl import logging
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_string("data_path", None, "Output location of data file.")
flags.DEFINE_string("webdriver", None, "Path to webdriver.")
flags.DEFINE_string("browser", None, "Path to web browser.")
flags.mark_flag_as_required("data_path")
flags.mark_flag_as_required("webdriver")
flags.mark_flag_as_required("browser")

logging.set_verbosity(logging.DEBUG)


def getStateName(responseText: str) -> str:
    """Parse state name in title field.

    Args:
        responseText: response.text object from requests.

    Returns: State string name.
    """
    soup = Soup(responseText, "html.parser")
    logging.debug("Ingesting soup: %s", soup.prettify())
    return soup.title.get_text()


def writeToFile(content: str, fileout: str) -> None:
    """File output handler.

    Args:
        content: Data to write to file.
        fileout: Path for file location.
    """
    soup = Soup(content, "html.parser")
    with open(fileout, "w") as dataFile:
        dataFile.write(soup.prettify())


def sendRequest(countryCode: str, stateId: int,
                bandId: int) -> requests.Response:
    """Prepare url and send ping to RepeaterBook.

    Args:
        courntryCode: Two letter country code.
        stateId: Repeater Book's special ID for each state.
        bandId: Repeater Books's special ID for bands.

    Returns: Response object.
    """
    res: requests.response = None
    try:
        url: str = ("https://www.repeaterbook.com/repeaters/Display_SS.php"
                    + f"?country_code={countryCode.upper()}&state_id={stateId}"
                    + f"&band={bandId}&loc=%&call=%&use=%")
        res = requests.get(url)
    except Exception as e:
        logging.warning("Could not ping RepeaterBook: %s", e)
    return res


def main(argv) -> None:
    logging.debug("Starting scrape...")

    # COUNTRY_CODE: str = "US"
    # STATE_ID: int = 53
    # BAND_ID: int = 14  # 2 meter

    response = sendRequest(countryCode="US", stateId=53, bandId=14)
    writeToFile(response.text, FLAGS.data_path)
    logging.info(getStateName(response.text))


if __name__ == "__main__":
    app.run(main)

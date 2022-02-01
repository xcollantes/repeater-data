"""Get data for repeaters."""

import json
import os
import requests
from absl import app
from absl import logging
from absl import flags

logging.set_verbosity(logging.DEBUG)
FLAGS = flags.FLAGS
flags.DEFINE_string("data_path", None, "Output location of data file.")


def scrape(argv) -> None:
    logging.debug("Strarting scrape...")
    COUNTRY_CODE: str = "US"
    STATE_ID: int = 53
    BASE_URL: str = ("https://www.repeaterbook.com/repeaters/index.php"
                     + f"?country_code={COUNTRY_CODE}&state_id={STATE_ID}"
                     + f"&loc=%&call=%&use=%")

    response = requests.get(BASE_URL)
    logging.info("RES: %s: %s", response.status_code, response.text)
    with open(FLAGS.data_path, "w") as dataFile:
        dataFile.write(response.text)


if __name__ == "__main__":
    app.run(scrape)

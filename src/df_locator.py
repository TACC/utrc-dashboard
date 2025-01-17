import logging

import pandas as pd

from src.data_functions import get_workbook_paths

logging.basicConfig(level=logging.DEBUG)

workbook_paths = get_workbook_paths("./assets/data/monthly_reports")

for index, path in enumerate(workbook_paths):
    workbook = pd.read_excel(path, sheet_name=None)
    filename = path.split("/")[-1]
    for worksheet in workbook:
        if worksheet == "utrc_new_grants":
            continue
        if "root_institution_name" not in workbook[worksheet].columns:
            logging.debug(filename)
            logging.debug(worksheet)
        if workbook[worksheet].empty:
            logging.debug("empty")

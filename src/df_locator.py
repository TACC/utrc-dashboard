import pandas as pd
from os import walk
import logging

logging.basicConfig(level=logging.DEBUG)


def get_workbook_paths(directory):
    f = []
    for (dirpath, _, filenames) in walk(directory):
        for filename in filenames:
            if filename.endswith('.xlsx'):
                f.append(dirpath + "/" + filename)
        break
    return f

workbook_paths = get_workbook_paths('./assets/data/monthly_reports')

for index, path in enumerate(workbook_paths):
        workbook = pd.read_excel(path, sheet_name=None)
        filename = path.split('/')[-1]
        for worksheet in workbook:
            if worksheet == 'utrc_new_grants':
                continue
            if 'root_institution_name' not in workbook[worksheet].columns:
                logging.debug(filename)
                logging.debug(worksheet)
            if workbook[worksheet].empty:
                 logging.debug('empty')
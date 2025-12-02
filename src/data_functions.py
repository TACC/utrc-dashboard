import logging
import re
from datetime import datetime
from os import walk
import pandas as pd
from fuzzywuzzy import fuzz
from src.constants import FISCAL_YEAR_MONTHS

from .constants import (
    COLUMN_HEADERS,
    COLUMN_ORDER,
    INSTITUTIONS,
    WORKSHEETS_RM_DUPLICATES,
)

logging.basicConfig(level=logging.INFO)


def fuzzy_match_institution(institution_input):
    top_score = 0
    top_institution = None
    for i in INSTITUTIONS.keys():
        current_score = fuzz.ratio(institution_input, i)
        if current_score > top_score:
            top_score = current_score
            top_institution = i
    logging.debug("Fuzzy match results:")
    logging.debug(f"Input: {institution_input}")
    logging.debug(f"Match: {top_institution}")
    logging.debug(f"Match score: {top_score}")
    return INSTITUTIONS[top_institution]


def get_fiscal_year_dates(fiscal_year):
    start = fiscal_year.split("-")[0]
    end = fiscal_year.split("-")[1]
    dates = []
    for month in FISCAL_YEAR_MONTHS["start_months"]:
        dates.append(f"{start}-{month}")
    for month in FISCAL_YEAR_MONTHS["end_months"]:
        dates.append(f"{end}-{month}")
    return dates


def get_all_months():
    options = create_fy_options()
    marks = []
    for fy in options:
        newmarks = get_marks(fy)
        marks_list = [x for x in newmarks.values()]
        marks.extend(marks_list)
    return marks


def get_workbook_paths(directory):
    f = []
    for dirpath, _, filenames in walk(directory):
        for filename in filenames:
            if filename.endswith(".xlsx"):
                f.append(dirpath + "/" + filename)
        break
    return f


def get_date_list(start, end):
    all_months = get_all_months()
    if start is None:
        start_idx = 0
    else:
        start_idx = all_months.index(start)
    if end is None:
        return all_months[start_idx:]
    else:
        end_idx = all_months.index(end)
        return all_months[start_idx : end_idx + 1]


def split_month(date):
    return date.split("-")[1]


def check_date_order(start_date: str, end_date: str) -> bool:
    """check that the start date is before the end date"""
    start = start_date.split("-")
    end = end_date.split("-")
    # if end year is after start year, order is ok
    if int(end[0]) > int(start[0]):
        return True
    elif int(end[0]) < int(start[0]):
        return False
    elif int(end[1]) >= int(start[1]):
        return True
    else:
        return False


def update_worksheet_columns(workbook, filename):
    for worksheet in workbook:
        workbook[worksheet]["Date"] = get_date_from_filename(filename)
        if worksheet == "utrc_corral_usage":
            workbook[worksheet] = normalize_storage_granted(workbook[worksheet])
    return workbook


def normalize_storage_granted(df):

    def update_units(row):
        if row["Storage Unit"].upper() == "GB":
            return row["Storage Granted"] / 1024.0
        elif row["Storage Unit"].upper() == "TB":
            return row["Storage Granted"]

    new_df = df.copy()

    if "Storage Granted (Gb)" in df.columns:
        new_df["Storage Granted (TB)"] = new_df["Storage Granted (Gb)"] / 1024.0
    elif "Storage Granted" in new_df.columns:
        new_df["Storage Granted (TB)"] = new_df.apply(update_units, axis=1)

    return new_df

def get_date_from_filename(filename, prefix="utrc_report"):
    pattern = re.compile("{}_(.*)_to_(.*).xlsx".format(prefix))
    match = pattern.match(filename)
    series_date = ""
    if match:
        start_date_str = match.group(1)
        date = datetime.strptime(start_date_str, "%Y-%m-%d")
        series_date = date.strftime("%y-%m")
    return series_date


def initialize_df(workbook_path, WORKSHEETS):
    """
    To keep the dashboard running quickly, data should be read in only once.
    """
    dataframes = pd.read_excel(workbook_path, WORKSHEETS)
    for worksheet in dataframes:
        if dataframes[worksheet].empty:
            continue
        clean_df(dataframes[worksheet])
        if worksheet in WORKSHEETS_RM_DUPLICATES:
            remove_duplicates(dataframes[worksheet])

    return dataframes


def clean_df(df):
    # Rename worksheet table header
    df.rename(columns=COLUMN_HEADERS, inplace=True)
    df.dropna(subset="Institution", inplace=True)
    df.drop(
        df.columns[df.columns.str.contains("unnamed", case=False)], axis=1, inplace=True
    )

    s = pd.Series([x for x in range(df.shape[0])])
    df.set_index(s, inplace=True)

    # Replace full institution names with abbreviations
    for i in range(df.shape[0]):
        try:
            df.loc[i, "Institution"] = INSTITUTIONS[df.loc[i, "Institution"]]
        except KeyError:
            df.loc[i, "Institution"] = fuzzy_match_institution(df.loc[i, "Institution"])


def remove_duplicates(df):
    # Remove duplicates from individual sheets
    try:
        df.drop_duplicates(subset=["Login"], inplace=True)
    except KeyError:
        pass  # Some worksheets do not have a login column


def filter_df(df, institutions, date_range, machines):
    filtered_df = df[df["Institution"].isin(institutions)]
    filtered_df = filter_by_machine(filtered_df, machines)
    filtered_df = filtered_df[filtered_df["Date"].isin(date_range)]

    filtered_df.sort_values(["Date", "Institution"], inplace=True)
    filtered_df = sort_columns(filtered_df)

    return filtered_df


def select_df(DATAFRAMES, dropdown_selection, institutions, date_range, machines):
    """Given a list of filter inputs, returns a filtered dataframe."""
    df = DATAFRAMES[dropdown_selection]
    df = filter_df(df, institutions, date_range, machines)
    return df


def filter_by_machine(df, machines):
    if "Resource" not in df.columns.tolist():
        return df
    try:
        df = df[df["Resource"].isin(machines)]
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        logging.debug(message)
    return df


def get_totals(DATAFRAMES, checklist, date_range, worksheets, machines):
    """Given a dictionary of dataframes, a checklist of selected universities,
    and a date range of selected months, returns a dictionary of total, active
    and idle users in the last selected month."""
    totals = {}
    for worksheet in worksheets:
        df = DATAFRAMES[worksheet]
        filtered_df = filter_df(df, checklist, date_range, machines)
        inst_grps = filtered_df.groupby(["Institution"])
        avgs = []
        for group in checklist:
            try:
                avgs.append(inst_grps.get_group((group,))["Date"].value_counts().mean())
            except KeyError:
                continue
        count = int(sum(avgs))

        if worksheet == "utrc_individual_user_hpc_usage":
            totals["active_users"] = count
        elif worksheet == "utrc_idle_users":
            totals["idle_users"] = count
        elif worksheet == "utrc_active_allocations":
            totals["active_allocations"] = count
        elif worksheet == "utrc_current_allocations":
            idle_df = filtered_df.loc[df["Idle Allocation?"] == "X"]
            totals["idle_allocations"] = idle_df.shape[0]
            totals["total_allocations"] = (
                totals["idle_allocations"] + totals["active_allocations"]
            )
            logging.debug("totals" + str(totals))

    return totals


def get_marks(fiscal_year):
    """Returns a dictionary, where keys are an integer representing a month,
    and values are a string representation of '%y-%m' (e.g. '21-09')"""
    marks = {}
    workbook_paths = get_workbook_paths("./assets/data/monthly_reports")
    workbook_paths.sort()
    count = 0
    for path in workbook_paths:
        filename = path.split("/")[-1]
        date = get_date_from_filename(filename)
        if date in get_fiscal_year_dates(fiscal_year):
            marks[count] = date
            count += 1
    return marks


def calc_monthly_avgs(df, institutions):
    inst_grps = df.groupby(["Institution"])
    df_with_avgs = {"Institution": [], "Date": [], "Resource": [], "Count": []}
    for inst in institutions:
        try:
            monthly_avg = inst_grps.get_group((inst,))["Date"].value_counts().mean()
            df_with_avgs["Institution"].append(inst)
            df_with_avgs["Date"].append("AVG")
            df_with_avgs["Count"].append(round(monthly_avg))
            df_with_avgs["Resource"].append("ALL")
            date_grps = inst_grps.get_group((inst,)).groupby(["Date"])
            for date in date_grps.groups.keys():
                machine_grps = date_grps.get_group((date,)).groupby(["Resource"])
                for machine in machine_grps.groups:
                    current_count = machine_grps.get_group((machine,)).shape[0]
                    df_with_avgs["Institution"].append(inst)
                    df_with_avgs["Resource"].append(machine)
                    df_with_avgs["Count"].append(round(current_count))
                    df_with_avgs["Date"].append(date)
        except KeyError:
            continue  # For some date ranges, even if an institution is checked, it doesn't appear in the data, throwing an error
    df_with_avgs = pd.DataFrame(df_with_avgs)
    df_with_avgs.sort_values(["Date", "Institution"], inplace=True)
    logging.debug(df_with_avgs.to_string())
    return df_with_avgs


def calc_corral_monthly_sums(df, institutions):
    inst_grps = df.groupby(["Institution"])
    dict_with_avgs = {"Institution": [], "Date": [], "Storage Granted (TB)": []}
    for inst in institutions:
        try:
            date_grps = inst_grps.get_group((inst,)).groupby(["Date"])
            for date in date_grps.groups.keys():
                monthly_sum = date_grps.get_group((date,))["Storage Granted (TB)"].sum()
                dict_with_avgs["Institution"].append(inst)
                dict_with_avgs["Storage Granted (TB)"].append(round(monthly_sum))
                dict_with_avgs["Date"].append(date)
        except KeyError:
            continue
    df_with_avgs = pd.DataFrame(dict_with_avgs)
    df_with_avgs.sort_values(["Date", "Institution"], inplace=True)
    return df_with_avgs


def calc_corral_monthly_sums_with_peaks(df, institutions):
    df_with_avgs = calc_corral_monthly_sums(df, institutions)
    df_with_peaks = add_peaks_to_corral_df(df_with_avgs, institutions)
    return df_with_peaks


def add_peaks_to_corral_df(df, institutions):
    inst_grps = df.groupby(["Institution"])
    for inst in institutions:
        try:
            peak = inst_grps.get_group((inst,))["Storage Granted (TB)"].max()
            df.loc[len(df.index)] = [inst, "PEAK", peak]
        except KeyError:
            continue
    return df


def calc_corral_total(df_with_peaks):
    # df_with_peaks is calculated by calc_corral_monthly_sums()
    total = df_with_peaks[df_with_peaks["Date"] == "PEAK"]["Storage Granted (TB)"].sum()
    logging.debug(df_with_peaks[df_with_peaks["Date"] == "PEAK"].to_string())
    return total


def calc_node_monthly_sums_no_machine(df, institution):
    dict_with_avgs = {"Institution": [], "Date": [], "SU's Charged": []}
    date_grps = df.groupby(["Date"])
    for date, group in date_grps:
        monthly_sum = group["SU's Charged"].sum()
        dict_with_avgs["Institution"].append(institution)
        dict_with_avgs["SU's Charged"].append(round(monthly_sum))
        dict_with_avgs["Date"].append(date[0])
    df_with_avgs = pd.DataFrame(dict_with_avgs)
    df_with_avgs.sort_values(["Date", "Institution"], inplace=True)
    return df_with_avgs


def calc_node_monthly_sums(df, institutions):
    inst_grps = df.groupby(["Institution"])
    dict_with_avgs = {"Institution": [], "Resource": [], "Date": [], "SU's Charged": []}
    for inst in institutions:
        try:
            date_grps = inst_grps.get_group((inst,)).groupby(["Date"])
            for date in date_grps.groups.keys():
                machine_grps = date_grps.get_group((date,)).groupby(["Resource"])
                for machine in machine_grps.groups:
                    monthly_sum = machine_grps.get_group((machine,))[
                        "SU's Charged"
                    ].sum()
                    dict_with_avgs["Institution"].append(inst)
                    dict_with_avgs["Resource"].append(machine)
                    dict_with_avgs["SU's Charged"].append(round(monthly_sum))
                    dict_with_avgs["Date"].append(date)
        except KeyError:
            continue
    df_with_avgs = pd.DataFrame(dict_with_avgs)
    df_with_avgs.sort_values(["Date", "Institution"], inplace=True)
    return df_with_avgs


def get_fy_for_month(date: str) -> str:
    datelist = date.split("-")
    year = datelist[0]
    month = datelist[1]
    if month in FISCAL_YEAR_MONTHS["start_months"]:
        fy = f"{year}-{int(year) + 1}"
    elif month in FISCAL_YEAR_MONTHS["end_months"]:
        fy = f"{int(year) - 1}-{year}"
    return fy


def get_first_or_last_month_in_fy(fy: str, which: str):
    if which == "first":
        month = FISCAL_YEAR_MONTHS["start_months"][0]
        year = fy.split("-")[0]
    elif which == "last":
        month = FISCAL_YEAR_MONTHS["end_months"][-1]
        year = fy.split("-")[1]
    return f"{year}-{month}"


def create_fy_options():
    paths = get_workbook_paths("./assets/data/monthly_reports")
    dates = []
    for path in paths:
        filename = path.split("/")[-1]
        dates.append(get_date_from_filename(filename))

    fy_options = []
    for date in dates:
        option = get_fy_for_month(date)
        if option not in fy_options:
            fy_options.append(option)
    fy_options.sort()

    return fy_options


def get_allocation_totals(DATAFRAMES, checklist, date_range, worksheets, machines):
    totals = {}
    for worksheet in worksheets:
        df = DATAFRAMES[worksheet]
        totals_df = filter_df(df, checklist, date_range, machines)
        logging.debug(worksheet)
        logging.debug(totals_df.head())
        if worksheet == "utrc_current_allocations":
            totals_df = totals_df.loc[totals_df["Idle Allocation?"] == "X"]
        inst_grps = totals_df.groupby(["Institution"])
        avgs = []
        for group in checklist:
            try:
                avgs.append(inst_grps.get_group((group,))["Date"].value_counts().mean())
            except KeyError:
                continue
        count = int(sum(avgs))

        if worksheet == "utrc_active_allocations":
            totals["active_allocations"] = count
        elif worksheet == "utrc_current_allocations":
            totals["idle_allocations"] = count
    logging.debug("totals" + str(totals))
    return totals


def sort_columns(df):
    df_columns = df.columns.tolist()
    final_order = []
    for item in COLUMN_ORDER:
        if item in df_columns:
            final_order.append(item)
    df = df[final_order]
    return df

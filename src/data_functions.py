import pandas as pd
import logging
from os import walk
import re
from datetime import datetime
from fuzzywuzzy import fuzz
from .constants import (
    REPORTS_PATH,
    INSTITUTIONS,
    COLUMN_HEADERS,
    COLUMN_ORDER,
    PROTECTED_COLUMNS,
    NODE_HOURS_MODIFIER,
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
    start_months = ["09", "10", "11", "12"]
    end = fiscal_year.split("-")[1]
    end_months = ["01", "02", "03", "04", "05", "06", "07", "08"]
    dates = []
    for month in start_months:
        dates.append(f"{start}-{month}")
    for month in end_months:
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


def append_date_to_worksheets(workbook, filename):
    for worksheet in workbook:
        workbook[worksheet]["Date"] = get_date_from_filename(filename)
    return workbook


def get_date_from_filename(filename, prefix="utrc_report"):
    # utrc_report_2017-01-01_to_2017-02-01.xlsx
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


def merge_workbooks(WORKSHEETS):
    workbook_paths = get_workbook_paths(REPORTS_PATH)
    for index, path in enumerate(workbook_paths):
        workbook = initialize_df(path, WORKSHEETS)
        filename = path.split("/")[-1]
        workbook = append_date_to_worksheets(workbook, filename)

        if index == 0:
            dict_of_dfs = workbook
        else:
            for sheet in WORKSHEETS:
                dict_of_dfs[sheet] = pd.concat([dict_of_dfs[sheet], workbook[sheet]])

    return dict_of_dfs


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
        except:
            df.loc[i, "Institution"] = fuzzy_match_institution(df.loc[i, "Institution"])


def remove_duplicates(df):
    # Remove duplicates from individual sheets
    try:
        df.drop_duplicates(subset=["Login"], inplace=True)
    except:
        pass  # Some worksheets do not have a login column


def filter_df(df, institutions, date_range, machines):
    filtered_df = df[df["Institution"].isin(institutions)]
    filtered_df = filter_by_machine(filtered_df, machines)
    filtered_df = filtered_df[filtered_df["Date"].isin(date_range)]

    filtered_df.sort_values(["Date", "Institution"], inplace=True)
    filtered_df = sort_columns(filtered_df)

    return filtered_df


def select_df(DATAFRAMES, dropdown_selection, institutions, date_range, machines):
    """Given a list of filter inputs, returns a filtered dataframe. Removes
    sensitive data if iframed into public view."""
    # print(dropdown_selection)
    df = DATAFRAMES[dropdown_selection]
    # print(df)

    # if iframed==True:
    #     for column in PROTECTED_COLUMNS:
    #         try:
    #             df = df.drop(columns=column)
    #         except: # Throws error if column name isn't in specific worksheets
    #             continue

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


def get_totals(DATAFRAMES, checklist, date_range, fiscal_year, worksheets, machines):
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
            except:
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
        except:
            continue  # For some date ranges, even if an institution is checked, it doesn't appear in the data, throwing an error
    df_with_avgs = pd.DataFrame(df_with_avgs)
    df_with_avgs.sort_values(["Date", "Institution"], inplace=True)
    logging.debug(df_with_avgs.to_string())
    return df_with_avgs


def calc_node_hours(df):
    for i in range(len(df)):
        df.loc[i, "SU's Charged"] = round(
            df.loc[i, "SU's Charged"] * NODE_HOURS_MODIFIER[df.loc[i, "Resource"]]
        )
    return df


def calc_node_fy_sums(df, institutions):
    inst_grps = df.groupby(["Institution"])
    df_with_avgs = {"Institution": [], "Date": [], "SU's Charged": []}
    for group in institutions:
        try:
            sum = inst_grps.get_group((group,))["SU's Charged"].sum()
            df_with_avgs["Institution"].append(group)
            df_with_avgs["SU's Charged"].append(round(sum))
            df_with_avgs["Date"].append("FYTD SUM")
        except:
            continue  # For some date ranges, even if an institution is checked, it doesn't appear in the data, throwing an error
    combined_df = pd.concat([df, pd.DataFrame(df_with_avgs)])
    return combined_df


def calc_corral_monthly_sums(df, institutions):
    inst_grps = df.groupby(["Institution"])
    df_with_avgs = {"Institution": [], "Date": [], "Storage Granted (TB)": []}
    for inst in institutions:
        try:
            date_grps = inst_grps.get_group((inst,)).groupby(["Date"])
            for date in date_grps.groups.keys():
                monthly_sum = date_grps.get_group((date,))["Storage Granted (Gb)"].sum()
                monthly_sum = int(round(monthly_sum / 1024.0))
                df_with_avgs["Institution"].append(inst)
                df_with_avgs["Storage Granted (TB)"].append(round(monthly_sum))
                df_with_avgs["Date"].append(date)
        except:
            continue
    df_with_avgs = pd.DataFrame(df_with_avgs)
    df_with_avgs.sort_values(["Date", "Institution"], inplace=True)
    df_with_peaks = add_peaks_to_corral_df(df_with_avgs, institutions)
    return df_with_peaks


def add_peaks_to_corral_df(df, institutions):
    inst_grps = df.groupby(["Institution"])
    for inst in institutions:
        try:
            peak = inst_grps.get_group((inst,))["Storage Granted (TB)"].max()
            df.loc[len(df.index)] = [inst, "PEAK", peak]
        except:
            continue
    return df


def calc_corral_total(df, institutions):
    df_with_peaks = calc_corral_monthly_sums(df, institutions)
    total = df_with_peaks[df_with_peaks["Date"] == "PEAK"]["Storage Granted (TB)"].sum()
    logging.debug(df_with_peaks[df_with_peaks["Date"] == "PEAK"].to_string())
    return total


def calc_node_monthly_sums(df, institutions):
    inst_grps = df.groupby(["Institution"])
    df_with_avgs = {"Institution": [], "Resource": [], "Date": [], "SU's Charged": []}
    for inst in institutions:
        try:
            date_grps = inst_grps.get_group((inst,)).groupby(["Date"])
            for date in date_grps.groups.keys():
                machine_grps = date_grps.get_group((date,)).groupby(["Resource"])
                for machine in machine_grps.groups:
                    monthly_sum = machine_grps.get_group((machine,))[
                        "SU's Charged"
                    ].sum()
                    df_with_avgs["Institution"].append(inst)
                    df_with_avgs["Resource"].append(machine)
                    df_with_avgs["SU's Charged"].append(round(monthly_sum))
                    df_with_avgs["Date"].append(date)
        except:
            continue
    df_with_avgs = pd.DataFrame(df_with_avgs)
    df_with_avgs.sort_values(["Date", "Institution"], inplace=True)
    return df_with_avgs


def create_fy_options():
    paths = get_workbook_paths("./assets/data/monthly_reports")
    dates = []
    for path in paths:
        filename = path.split("/")[-1]
        dates.append(get_date_from_filename(filename))

    fy_options = []
    start_months = ["09", "10", "11", "12"]
    end_months = ["01", "02", "03", "04", "05", "06", "07", "08"]
    for date in dates:
        year = date.split("-")[0]
        month = date.split("-")[1]
        if month in start_months:
            option = f"{year}-{int(year)+1}"
        elif month in end_months:
            option = f"{int(year)-1}-{year}"
        if option not in fy_options:
            fy_options.append(option)
    fy_options.sort()

    return fy_options


def get_allocation_totals(
    DATAFRAMES, checklist, date_range, fiscal_year, worksheets, machines
):
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
            except:
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

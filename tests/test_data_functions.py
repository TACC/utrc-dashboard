import pandas as pd

from src.data_functions import (
    calc_corral_monthly_sums,
    calc_corral_total,
    calc_monthly_avgs,
    calc_node_monthly_sums,
    create_fy_options,
    get_allocation_totals,
    get_date_list,
    get_totals,
    select_df,
)


# General purpose functions
def test_create_fy_options():
    # This will break whenever a new fiscal year is added to the data
    t1 = create_fy_options()
    assert t1 == ["22-23", "23-24"]


def test_get_date_list():
    # This may break if spreadsheet data changes
    r1 = ["23-11", "23-12"]
    t1 = get_date_list("23-11", "23-12")
    assert t1 == r1

    r2 = [
        "23-01",
        "23-02",
        "23-03",
        "23-04",
        "23-05",
        "23-06",
        "23-07",
        "23-08",
        "23-09",
        "23-10",
        "23-11",
        "23-12",
    ]
    t2 = get_date_list("23-01", "23-12")
    assert t2 == r2


def test_select_df():
    d1 = {
        "Institution": ["UTAus", "UTA", "UTD", "UTAus", "UTPB", "UTRGV", "UTAus"],
        "Date": ["23-01", "23-02", "23-02", "23-02", "23-02", "23-02", "23-02"],
        "Machine": [
            "Lonestar6",
            "Frontera",
            "Longhorn3",
            "Stampede4",
            "Lonestar5",
            "Maverick3",
            "Jetstream",
        ],
        "Storage Granted (TB)": [x for x in range(7)],
    }
    df1 = pd.DataFrame(data=d1)

    d2 = {
        "Institution": ["UTAus", "UTAus", "UTAus", "UTAus", "UTPB", "UTRGV", "UTD"],
        "Name": [
            "Corral2",
            "Corral-Protected",
            "Corral2",
            "Corral-Protected",
            "Corral2",
            "Corral-Protected",
            "Corral2",
        ],
        "Last Name": ["Smith", "Doe", "Garcia", "Nguyen", "Brown", "Lee", "Johnson"],
        "First Name": ["John", "Jill", "Jose", "James", "Joe", "Jade", "Janice"],
        "Email": [
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
        ],
        "Login": ["uname", "uname", "uname", "uname", "uname", "uname", "uname"],
        "Project Name": ["name", "name", "name", "name", "name", "name", "name"],
        "Title": [
            "title",
            "title",
            "title",
            "title",
            "title",
            "title",
            "title",
        ],
        "Project Type": [
            "Partner",
            "Research",
            "Partner",
            "Research",
            "Partner",
            "Research",
            "Research",
        ],
        "Start Date": ["22-01", "22-03", "23-01", "23-01", "23-01", "23-01", "23-01"],
        "End Date": ["23-12", "23-12", "23-12", "23-12", "23-12", "23-12", "23-12"],
        "Status": [
            "Active",
            "Active",
            "Active",
            "Active",
            "Active",
            "Active",
            "Active",
        ],
        "Storage Granted (Gb)": [1000, 100, 200, 500, 600, 2000, 700],
        "New PI?": [None, None, None, None, None, None, None],
        "Date": ["23-01", "23-12", "23-12", "23-12", "23-12", "23-12", "23-12"],
    }
    df2 = pd.DataFrame(data=d2)
    DATAFRAMES = {"utrc_active_allocations": df1, "utrc_corral_usage": df2}

    d3 = {
        "Institution": ["UTAus"],
        "Storage Granted (TB)": [0],
        "Date": ["23-01"],
    }
    r1 = pd.DataFrame(data=d3)
    t1 = select_df(
        DATAFRAMES, "utrc_active_allocations", ["UTAus"], ["23-01"], ["Lonestar6"]
    )
    assert t1.equals(r1)

    d4 = {
        "Institution": ["UTAus"],
        "Storage Granted (Gb)": [1000],
        "Last Name": ["Smith"],
        "First Name": ["John"],
        "Name": ["Corral2"],
        "Email": ["test@abc.com"],
        "Project Name": ["name"],
        "Title": ["title"],
        "Project Type": ["Partner"],
        "Login": ["uname"],
        "New PI?": [None],
        "Start Date": ["22-01"],
        "End Date": ["23-12"],
        "Status": ["Active"],
        "Date": ["23-01"],
    }
    r2 = pd.DataFrame(data=d4)
    t2 = select_df(DATAFRAMES, "utrc_corral_usage", ["UTAus"], ["23-01"], ["Lonestar6"])
    assert t2.equals(r2)


# Functions that are used in allocations.py
def test_calc_monthly_avgs():
    # df for t1
    d1 = {
        "Institution": ["UTAus", "UTAus", "UTD", "UTAus", "UTPB", "UTRGV", "UTAus"],
        "Date": ["23-01", "23-01", "23-02", "23-02", "23-02", "23-02", "23-02"],
        "Machine": [
            "Lonestar6",
            "Frontera",
            "Longhorn3",
            "Stampede4",
            "Lonestar5",
            "Maverick3",
            "Jetstream",
        ],
        "Storage Granted (TB)": [x for x in range(7)],
    }
    df1 = pd.DataFrame(data=d1)

    # df for r1
    d2 = {
        "Institution": ["UTAus"],
        "Date": ["AVG"],
        "Resource": ["ALL"],
        "Count": 2,
    }
    r1 = pd.DataFrame(data=d2)
    t1 = calc_monthly_avgs(df1, ["UTAus"])
    assert t1.equals(r1)

    # df for t2
    d3 = {
        "Institution": ["UTAus", "UTAus", "UTD", "UTD", "UTPB", "UTRGV", "UTAus"],
        "Date": ["23-01", "23-01", "23-02", "23-02", "23-02", "23-02", "23-02"],
        "Machine": [
            "Lonestar6",
            "Frontera",
            "Longhorn3",
            "Stampede4",
            "Lonestar5",
            "Maverick3",
            "Jetstream",
        ],
        "Storage Granted (TB)": [x for x in range(7)],
    }
    df3 = pd.DataFrame(data=d3)
    # df for r2
    d4 = {
        "Institution": ["UTAus", "UTD"],
        "Date": ["AVG", "AVG"],
        "Resource": ["ALL", "ALL"],
        "Count": [2, 2],
    }
    r2 = pd.DataFrame(data=d4)
    t2 = calc_monthly_avgs(df3, ["UTAus", "UTD"])
    assert t2.equals(r2)


def test_get_allocation_totals():
    d1 = {
        "Institution": ["UTAus", "UTA", "UTD", "UTAus", "UTPB", "UTRGV", "UTAus"],
        "Date": ["23-01", "23-02", "23-02", "23-02", "23-02", "23-02", "23-02"],
        "Machine": [
            "Lonestar6",
            "Frontera",
            "Lonestar6",
            "Stampede4",
            "Lonestar5",
            "Maverick3",
            "Jetstream",
        ],
        "Storage Granted (TB)": [x for x in range(7)],
    }
    df1 = pd.DataFrame(data=d1)

    d2 = {
        "Institution": ["UTAus", "UTAus", "UTAus", "UTAus", "UTPB", "UTRGV", "UTD"],
        "Resource": [
            "Lonestar6",
            "Frontera",
            "Lonestar6",
            "Stampede4",
            "Lonestar5",
            "Maverick3",
            "Jetstream",
        ],
        "Type": ["VIS", "HPC", "VIS", "HPC", "VIS", "HPC", "VIS"],
        "Last Name": ["Smith", "Doe", "Garcia", "Nguyen", "Brown", "Lee", "Johnson"],
        "First Name": ["John", "Jill", "Jose", "James", "Joe", "Jade", "Janice"],
        "Email": [
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
        ],
        "Login": ["uname", "uname", "uname", "uname", "uname", "uname", "uname"],
        "Project Name": ["name", "name", "name", "name", "name", "name", "name"],
        "Title": [
            "title",
            "title",
            "title",
            "title",
            "title",
            "title",
            "title",
        ],
        "Project Type": [
            "Partner",
            "Research",
            "Partner",
            "Research",
            "Partner",
            "Research",
            "Research",
        ],
        "Total Granted": [100, 1000, 2000, 4000, 600, 200, 800],
        "Total Refunded": [0, 0, 0, 1000, 0, 0, 0],
        "Total Used": [50, 500, 800, 3000, 300, 100, 600],
        "Balance": [50, 500, 200, 1000, 300, 100, 200],
        "Start Date": ["22-01", "22-03", "23-01", "23-01", "23-01", "23-01", "23-01"],
        "End Date": ["23-12", "23-12", "23-12", "23-12", "23-12", "23-12", "23-12"],
        "Status": [
            "Active",
            "Inactive",
            "Active",
            "Active",
            "Active",
            "Active",
            "Active",
        ],
        "New PI?": [None, None, None, None, None, None, None],
        "Idle Allocation?": [None, "X", None, None, None, None, None],
        "Date": ["23-01", "23-12", "23-12", "23-12", "23-12", "23-12", "23-12"],
    }

    df2 = pd.DataFrame(data=d2)
    DATAFRAMES = {"utrc_active_allocations": df1, "utrc_current_allocations": df2}
    r1 = {"active_allocations": 1, "idle_allocations": 1}
    t1 = get_allocation_totals(
        DATAFRAMES,
        ["UTAus", "UTD"],
        ["23-01", "23-12"],
        ["utrc_active_allocations", "utrc_current_allocations"],
        ["Lonestar6", "Frontera"],
    )
    assert t1 == r1


# Functions that are used in usage.py
def test_calc_node_monthly_sums():
    d1 = {
        "Institution": ["UTAus", "UTAus", "UTAus", "UTAus", "UTPB", "UTRGV", "UTD"],
        "Resource": [
            "Lonestar6",
            "Frontera",
            "Lonestar6",
            "Stampede4",
            "Lonestar5",
            "Maverick3",
            "Jetstream",
        ],
        "Type": ["VIS", "HPC", "VIS", "HPC", "VIS", "HPC", "VIS"],
        "SU's Charged": [1, 2, 3, 4, 5, 6, 7],
        "Last Name": ["Smith", "Doe", "Garcia", "Nguyen", "Brown", "Lee", "Johnson"],
        "First Name": ["John", "Jill", "Jose", "James", "Joe", "Jade", "Janice"],
        "Email": [
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
        ],
        "Project Name": ["name", "name", "name", "name", "name", "name", "name"],
        "Title": [
            "title",
            "title",
            "title",
            "title",
            "title",
            "title",
            "title",
        ],
        "Project Type": [
            "Partner",
            "Research",
            "Partner",
            "Research",
            "Partner",
            "Research",
            "Research",
        ],
        "Job Count": [1, 2, 3, 4, 5, 6, 7],
        "User Count": [1, 2, 3, 4, 5, 6, 7],
        "Login": ["uname", "uname", "uname", "uname", "uname", "uname", "uname"],
        "New PI?": [None, None, None, None, None, None, None],
        "Date": ["23-01", "23-12", "23-12", "23-12", "23-12", "23-12", "23-12"],
    }
    df1 = pd.DataFrame(data=d1)
    d2 = {
        "Institution": ["UTAus", "UTAus", "UTAus", "UTAus", "UTD"],
        "Resource": [
            "Lonestar6",
            "Frontera",
            "Lonestar6",
            "Stampede4",
            "Jetstream",
        ],
        "Date": ["23-01", "23-12", "23-12", "23-12", "23-12"],
        "SU's Charged": [1, 2, 3, 4, 7],
    }
    r1 = pd.DataFrame(data=d2)
    t1 = calc_node_monthly_sums(df1, ["UTAus", "UTD"])
    assert t1.equals(r1)


def test_calc_corral_monthly_sums():
    d1 = {
        "Institution": ["UTAus", "UTAus", "UTAus", "UTAus", "UTPB", "UTRGV", "UTD"],
        "Storage Granted (Gb)": [x * 1000 for x in range(7)],
        "Last Name": ["Smith", "Doe", "Garcia", "Nguyen", "Brown", "Lee", "Johnson"],
        "First Name": ["John", "Jill", "Jose", "James", "Joe", "Jade", "Janice"],
        "Name": [
            "Corral2",
            "Corral-Protected",
            "Corral2",
            "Corral-Protected",
            "Corral2",
            "Corral-Protected",
            "Corral2",
        ],
        "Email": [
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
        ],
        "Project Name": ["name", "name", "name", "name", "name", "name", "name"],
        "Title": [
            "title",
            "title",
            "title",
            "title",
            "title",
            "title",
            "title",
        ],
        "Project Type": [
            "Partner",
            "Research",
            "Partner",
            "Research",
            "Partner",
            "Research",
            "Research",
        ],
        "Login": ["uname", "uname", "uname", "uname", "uname", "uname", "uname"],
        "New PI?": [None, None, None, None, None, None, None],
        "Start Date": ["22-01", "22-03", "23-01", "23-01", "23-01", "23-01", "23-01"],
        "End Date": ["23-12", "23-12", "23-12", "23-12", "23-12", "23-12", "23-12"],
        "Status": [
            "Active",
            "Inactive",
            "Active",
            "Active",
            "Active",
            "Active",
            "Active",
        ],
        "Date": ["23-01", "23-02", "23-02", "23-03", "23-12", "23-12", "23-12"],
    }
    df1 = pd.DataFrame(data=d1)
    d2 = {
        "Institution": ["UTAus", "UTAus", "UTAus", "UTAus"],
        "Date": ["23-01", "23-02", "23-03", "PEAK"],
        "Storage Granted (TB)": [0, 3, 3, 3],
    }
    r1 = pd.DataFrame(data=d2)
    t1 = calc_corral_monthly_sums(df1, ["UTAus"])
    assert t1.equals(r1)


def test_calc_corral_total():
    # same as result of test_calc_corral_monthly_sums
    d1 = {
        "Institution": ["UTAus", "UTAus", "UTAus", "UTAus"],
        "Date": ["23-01", "23-02", "23-03", "PEAK"],
        "Storage Granted (TB)": [0, 3, 3, 3],
    }
    df1 = pd.DataFrame(data=d1)
    t1 = calc_corral_total(df1)
    assert t1 == 3


# Functions used in users.py
def test_get_totals():
    d1 = {
        "Institution": ["UTAus", "UTAus", "UTAus", "UTAus", "UTPB", "UTRGV", "UTD"],
        "Resource": [
            "Lonestar6",
            "Frontera",
            "Lonestar6",
            "Stampede4",
            "Lonestar5",
            "Maverick3",
            "Jetstream",
        ],
        "Type": ["VIS", "HPC", "VIS", "HPC", "VIS", "HPC", "VIS"],
        "Last Name": ["Smith", "Doe", "Garcia", "Nguyen", "Brown", "Lee", "Johnson"],
        "First Name": ["John", "Jill", "Jose", "James", "Joe", "Jade", "Janice"],
        "Login": ["uname", "uname", "uname", "uname", "uname", "uname", "uname"],
        "Email": [
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
        ],
        "Project Name": ["name", "name", "name", "name", "name", "name", "name"],
        "Title": [
            "title",
            "title",
            "title",
            "title",
            "title",
            "title",
            "title",
        ],
        "Project Type": [
            "Partner",
            "Research",
            "Partner",
            "Research",
            "Partner",
            "Research",
            "Research",
        ],
        "Job Count": [x * 10 for x in range(7)],
        "Date": ["23-01", "23-02", "23-02", "23-03", "23-12", "23-12", "23-12"],
    }

    d2 = {
        "Institution": ["UTAus", "UTAus", "UTAus", "UTAus", "UTPB", "UTRGV", "UTD"],
        "Last Name": ["Smith", "Doe", "Garcia", "Nguyen", "Brown", "Lee", "Johnson"],
        "First Name": ["John", "Jill", "Jose", "James", "Joe", "Jade", "Janice"],
        "Email": [
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
            "test@abc.com",
        ],
        "Login": ["uname", "uname", "uname", "uname", "uname", "uname", "uname"],
        "Account Type": [
            "Individual",
            "Individual",
            "Individual",
            "Service",
            "Individual",
            "Individual",
            "Individual",
        ],
        "Account Status": [
            "Active",
            "Deactivated",
            "Active",
            "Active",
            "Active",
            "Active",
            "Active",
        ],
        "Date": ["23-01", "23-02", "23-02", "23-03", "23-12", "23-12", "23-12"],
    }
    df1 = pd.DataFrame(data=d1)
    df2 = pd.DataFrame(data=d2)
    DATAFRAMES = {"utrc_individual_user_hpc_usage": df1, "utrc_idle_users": df2}

    r1 = {"active_users": 1, "idle_users": 1}
    t1 = get_totals(
        DATAFRAMES,
        ["UTAus", "UTD"],
        ["23-01", "23-02"],
        ["utrc_individual_user_hpc_usage", "utrc_idle_users"],
        ["Lonestar6", "Frontera"],
    )
    assert t1 == r1

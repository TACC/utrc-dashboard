from src.data_functions import merge_workbooks

WORKSHEETS = [
    "utrc_individual_user_hpc_usage",
    "utrc_new_users",
    "utrc_idle_users",
    "utrc_suspended_users",
    "utrc_active_allocations",
    "utrc_current_allocations",
    "utrc_new_allocation_requests",
    "utrc_corral_usage",
]

DATAFRAMES = merge_workbooks(WORKSHEETS)

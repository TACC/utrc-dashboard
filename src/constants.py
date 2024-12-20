REPORTS_PATH = "assets/data/monthly_reports"

INSTITUTIONS = {
    "The University of Texas": "UTAus",
    "The University of Texas in El Paso": "UTEP",
    "The University of Texas at El Paso School of Pharmacy": "UTEP",
    "University of Texas at Austin": "UTAus",
    "University of Texas - Austin": "UTAus",
    "University of Texas, Austin": "UTAus",
    "The University of Texas at Austin": "UTAus",
    "The University of Texas Austin": "UTAus",
    "Dell Medical School, University of Texas at Austin": "UTAus",
    "University of Texas-Austin": "UTAus",
    "University of Texas at Arlington": "UTA",
    "University of Texas Arlington": "UTA",
    "The University of Texas at Arlington": "UTA",
    "University of Texas at Dallas": "UTD",
    "The University of Texas at Dallas": "UTD",
    "University of Texas, Dallas": "UTD",
    "University of Texas at El Paso": "UTEP",
    "The University of Texas at El paso": "UTEP",
    "University of Texas, El Paso": "UTEP",
    "University of Texas of the Permian Basin": "UTPB",
    "University of Texas Rio Grande Valley": "UTRGV",
    "The University of Texas - Rio Grande Valley": "UTRGV",
    "The University of Texas Rio Grande Valley": "UTRGV",
    "University of Texas - Rio Grande Valley": "UTRGV",
    "University of Texas at Rio Grande Valley": "UTRGV",
    "University of Texas Rio Grade Valley": "UTRGV",
    "University of Texas at San Antonio": "UTSA",
    "The University of Texas at San Antonio": "UTSA",
    "University of Texas at Tyler": "UTT",
    "University of Texas Health Science Center at Houston": "UTHSC-H",
    "The University of Texas Health Science Center at Houston": "UTHSC-H",
    "University of Texas, Houston": "UTHSC-H",
    "University of Texas Health Science Center at San Antonio": "UTHSC-SA",
    "University of Texas Health Science Center, San Antonio": "UTHSC-SA",
    "University of Texas Health Science Center in San Antonio": "UTHSC-SA",
    "University of Texas Health Science Center at Tyler": "UTT",
    "University of Texas Medical Branch": "UTMB",
    "University of Texas M. D. Anderson Cancer Center": "UTMDA",
    "University of Texas MD Anderson Cancer Center": "UTMDA",
    "The University of Texas MD Anderson Cancer Center": "UTMDA",
    "University of Texas Southwestern Medical Center": "UTSW",
    "University of Texas at Brownsville": "UTRGV",
    "University of Texas Pan-American": "UTRGV",
    "University of Texas System": "UTSYS",
    "University of Texas System Administration": "UTSYS",
    "The University of Texas System Administration": "UTSYS",
    "University of Texas at Arlington (UTA) (UT Arlington)": "UTA",
    "University of Texas at Austin (UT) (UT Austin)": "UTAus",
    "University of Texas at Austin Dell Medical School": "UTAus",
    "University of Texas at Dallas (UTD) (UT Dallas)": "UTD",
    "University of Texas at El Paso (UTEP)": "UTEP",
    # "University of Texas at San Antonio": "UTSA",
    # "University of Texas Health Science Center at Houston": "UTHSC-H",
    # "University of Texas Health Science Center at San Antonio": "UTHSC-SA",
    # "University of Texas Health Science Center at Tyler": "UTT",
    "The University of Texas Health Science Center at Tyler": "UTT",
    # "University of Texas MD Anderson Cancer Center": "UTMDA",
    "University of Texas Medical Branch at Galveston": "UTMB",
    "University of Texas Permian Basin": "UTPB",
    # "University of Texas Rio Grande Valley": "UTRGV",
    "University of Texas Southwestern Medical Center (UTSW) (UT Southwestern)": "UTSW",
    # "University of Texas System": "UTSYS",
    "University of Texas Tyler": "UTT",
    "UTAus": "UTAus",
    "UTA": "UTA",
    "UTMDA": "UTMDA",
    "UTD": "UTD",
    "UTSW": "UTSW",
    "UTSA": "UTSA",
    "UTT": "UTT",
    "UTSYS": "UTSYS",
    "UTHSC-H": "UTHSC-H",
    "UTHSC-SA": "UTHSC-SA",
    "UTMB": "UTMB",
    "UTPB": "UTPB",
    "UTRGV": "UTRGV",
    "UTEP": "UTEP",
}

COLUMN_HEADERS = {
    "root_institution_name": "Institution",
    "last_name": "Last Name",
    "first_name": "First Name",
    "email": "Email",
    "login": "Login",
    "account_id": "Account ID",
    "account_type": "Account Type",
    "active_date": "Active Date",
    "changed": "Changed",
    "comment": "Comment",
    "resource_name": "Resource",
    "resource_type": "Type",
    "project_name": "Project Name",
    "title": "Title",
    "project_type": "Project Type",
    "jobs": "Job Count",
    "sus_charged": "SU's Charged",
    "users": "User Count",
    "New PI?": "New PI?",
    "New User?": "New User?",
    "Suspended User?": "Suspended?",
    "name": "Name",
    "start_date": "Start Date",
    "end_date": "End Date",
    "status": "Status",
    "storage_granted_gb": "Storage Granted (Gb)",
    "total_granted": "Total Granted",
    "total_refunded": "Total Refunded",
    "total_used": "Total Used",
    "balance": "Balance",
    "Idle Allocation?": "Idle Allocation?",
    "primary_field": "Primary Field",
    "secondary_field": "Secondary Field",
    "grant_title": "Grant Title",
    "funding_agency": "Funding Agency",
    "pi_name": "PI Name",
    "project_pi_last_name": "PI Last Name",
    "project_pi_first_name": "PI First Name",
    "project_pi_email": "PI Email",
    "project_title": "Project Title",
    "publication_id": "Publication ID",
    "year_published": "Year Published",
    "publisher": "Publisher",
    "account_status": "Account Status",
}

COLUMN_ORDER = [
    "Institution",
    "Resource",
    "Type",
    "SU's Charged",
    "Storage Granted (Gb)",
    "Storage Granted (TB)",
    "Total Granted",
    "Total Refunded",
    "Total Used",
    "Balance",
    "Last Name",
    "First Name",
    "Name",
    "PI Name",
    "PI Last Name",
    "PI First Name",
    "PI Email",
    "Email",
    "Project Name",
    "Title",
    "Project Title",
    "Project Type",
    "Job Count",
    "User Count",
    "Login",
    "Account ID",
    "Account Type",
    "Active Date",
    "Changed",
    "Comment",
    "New PI?",
    "New User?",
    "Suspended?",
    "Start Date",
    "End Date",
    "Status",
    "Idle Allocation?",
    "Primary Field",
    "Secondary Field",
    "Grant Title",
    "Funding Agency",
    "Publication ID",
    "Year Published",
    "Publisher",
    "Account Status",
    "Date",
]

PROTECTED_COLUMNS = [
    "email",
    "Email",
    "login",
    "Login",
    "account_id",
    "Account ID",
    "project_pi_email",
    "PI Email",
    "last_name",
    "Last Name",
    "first_name",
    "First Name",
]

NODE_HOURS_MODIFIER = {
    "Longhorn2": 0,
    "Stampede3": 0,
    "Maverick2": 0,
    "Jetstream": 0.04,
    "Chameleon": 0.04,
    "Lonestar4": 0,
    "Lonestar5": 1,  # everything relative to LS5
    "Wrangler3": 0,
    "Stampede4": 2,
    "Hikari": 0.04,
    "Maverick3": 1,
    "Frontera": 3,
    "Longhorn3": 3,
    "lonestar6": 4.5,
    "Lonestar6": 4.5,
}

WORKSHEETS_RM_DUPLICATES = [
    "utrc_individual_user_hpc_usage",
    "utrc_new_users",
    "utrc_idle_users",
]

from datetime import datetime, date, timedelta
import gspread_formatting as gsf
import colorsys 

# This file stores global constants for this scheduling algorithm, such as
# schedule params, constraints, and encodings
# All values here are constant and should not be edited


# TIMING CONSTANTS #######################################################

# Weekly CSIL schedule opening/closing times, can be edited for alternative hours
# Index 0 = Monday, and this indexing style is found in any array representing a week
CSIL_OPEN_TIMES = [("09:00", "23:00"),
                   ("09:00", "23:00"),
                   ("09:00", "23:00"),
                   ("09:00", "23:00"),
                   ("09:00", "23:00"),
                   ("12:00", "22:00"),
                   ("12:00", "22:00")]

# Smallest scheduling unit, in minutes, default is 30 min
BLOCK_LEN = 30
BLOCKS_PER_HOUR = int(60 // BLOCK_LEN)

# Calculates the number of shift blocks per day based on CSIL_OPEN_TIMES and BLOCK_LEN
BLOCKS_PER_DAY = [(datetime.combine(datetime.min, datetime.strptime(e, '%H:%M').time()) -
                   datetime.combine(datetime.min, datetime.strptime(s, '%H:%M').time())) //
                  timedelta(minutes=BLOCK_LEN)
                  for (s, e) in CSIL_OPEN_TIMES]

# Just for parsing, how many blocks to skip on the weekends in the when2meet
BLOCK_SKIP_WEEKEND_MORNING = 3 * BLOCKS_PER_HOUR
BLOCK_SKIP_WEEKEND_NIGHT = 1 * BLOCKS_PER_HOUR

# Precalculates the timestamps for each block, used in visualization
CSIL_TIMESTAMPS_PER_BLOCK = [[(datetime.strptime(s, "%H:%M") + timedelta(
    minutes=BLOCK_LEN * i)).strftime("%H:%M") for i in range(b + 1)] for (s, _), b in zip(CSIL_OPEN_TIMES, BLOCKS_PER_DAY)]

CSIL_START_TIMESTAMPS = [x[:-1] for x in CSIL_TIMESTAMPS_PER_BLOCK]

CSIL_END_TIMESTAMPS = [x[1:] for x in CSIL_TIMESTAMPS_PER_BLOCK]

# This year for calculating seniority
THIS_YEAR = int(date.today().year)


# SCHEDULE CONSTRAINTS CONSTANTS #######################################################

# The min/max number of tutors needed on shift
MIN_TUTORS_ON_SHIFT = 2
MAX_TUTORS_ON_SHIFT = 4

SHORT_SHIFT_LEN = 2 * BLOCKS_PER_HOUR
LONG_SHIFT_LEN = 4 * BLOCKS_PER_HOUR


# ENCODING CONSTANTS #######################################################

# The program encoding of the conflict/preference per block response from the google form
CONFLICT_TERMS_CODES = {"No conflict, not preferred": 0,
                        "Preferred shift": 1, "Conflict": 2}

# The set of allowed form responses to the conflict/preference per block question
FORM_CONFLICT_TERMS = set(CONFLICT_TERMS_CODES.keys())

# The program encoding of the preferred shift length response from the google form
SHIFT_LEN_CODES = {"No preference!": 0,
                   "Longer shifts (fewer days)": 1, "Shorter shifts (more days)": 2}

# The current set of teams at CSIL
CSIL_TEAMS = set(['Education/Instruction', 'Imaging', 'Inventory', 'Logins/Security',
                 'Merch', 'Servers', 'Activity Monitoring', 'Web-int', 'Website', 'Wiki'])

CSIL_TEAM_CODES = {x: i for i, x in enumerate(tuple(CSIL_TEAMS))}

# Google Sheets constants
SHEET_NAME = "CSIL Auto Generated Weekly Tutor Schedule"
SHEET_COLORS = [gsf.Color(*cs) for cs in [colorsys.hsv_to_rgb(x * 1.0/30, 0.334, 0.87) for x in range(30)]]

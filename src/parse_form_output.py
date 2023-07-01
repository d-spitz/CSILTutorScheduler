import tutor_info
import csil_tutors_info
import csv
import schedule
import const_csil_params

# This class parses csv output of the scheduling google forms/when2meets into a usable encoded
# CSILTutorsInfo object. All methods are static

# Given the when2meet csv output files and a tutor name, parses their conflicts/preferences and
# Writes it to a schedule manually and returns that schedule 
# When2meets start on sunday so that's annoying but accounted for
# 15-minute increments are ignored, as block size is 30 mins
# In the csv, 1 means the value was highlighted, else 0, so
# A 0 in availibility is a conflict, and a 1 in preference is a preference.
# This parsing works, but is ugly, could use improvement
def generate_conflicts_preferences(name, availibility_filepath, preferred_filepath):
    conf_pref_sched = schedule.Schedule() # This is a local schedule, stores int codes rather than tutor sets
    with open(preferred_filepath, newline='', encoding = 'cp850') as pref_file:
        rd = csv.reader(pref_file)
        tutor_col = 0
        d = -1
        b = 0
        day_beg_skip_count = 0
        day_end_skip_count = 0
        on_weekend = False
        skip_fix = False
        for i, row in enumerate(rd):
            # if i % 2 != 0:
            #     print(row)
            if i == 0:
                try:
                    row = [x.lower() for x in row]
                    tutor_col = row.index(name.lower())
                except:
                    print("Tutor " + name + " did not fill out the preference poll")
                    break
            elif i % 2 == 0:
                pass # skip over quarter hour availibility
            elif (on_weekend or row[0].startswith("Sunday") or row[0].startswith("Saturday")) and day_beg_skip_count < const_csil_params.BLOCK_SKIP_WEEKEND_MORNING:
                # print("beg_skip", on_weekend, day_beg_skip_count, day_end_skip_count, b)
                on_weekend = True
                day_beg_skip_count += 1
                pass
            elif day_end_skip_count == 0:
                if b >= const_csil_params.BLOCKS_PER_DAY[d]:
                    b = 0
                    d += 1
                    if not skip_fix and row[0].startswith("Saturday"):
                        skip_fix = True
                        pref_val = int(row[tutor_col])
                        # print("day:", d % 7, "block:", b, "pref_val:", int(row[tutor_col]))
                        if pref_val == 1: 
                            conf_pref_sched.state[d][b] = const_csil_params.CONFLICT_TERMS_CODES["Preferred shift"]
                        b += 1
                    else:
                        if on_weekend:
                            day_end_skip_count = 1
                        else:
                            pref_val = int(row[tutor_col])
                            # print("day:", d % 7, "block:", b, "pref_val:", int(row[tutor_col]))
                            if pref_val == 1: 
                                conf_pref_sched.state[d][b] = const_csil_params.CONFLICT_TERMS_CODES["Preferred shift"]
                            b += 1
                else:
                    pref_val = int(row[tutor_col])
                    # print("day:", d % 7, "block:", b, "pref_val:", int(row[tutor_col]))
                    if pref_val == 1: 
                        conf_pref_sched.state[d][b] = const_csil_params.CONFLICT_TERMS_CODES["Preferred shift"]
                    b += 1
            else:
                # print("end_skip", on_weekend, day_beg_skip_count, day_end_skip_count)
                if day_end_skip_count == const_csil_params.BLOCK_SKIP_WEEKEND_NIGHT - 1:
                    day_end_skip_count = 0
                    day_beg_skip_count = 0
                    on_weekend = False
                else:
                    day_end_skip_count += 1
                pass

    with open(availibility_filepath, newline='', encoding = 'cp850') as avail_file:
        rd = csv.reader(avail_file)
        tutor_col = 0
        d = -1
        b = 0
        day_beg_skip_count = 0
        day_end_skip_count = 0
        on_weekend = False
        skip_fix = False
        for i, row in enumerate(rd):
            # if i % 2 != 0:
            #     print(row)
            if i == 0:
                try:
                    tutor_col = row.index(name)
                except:
                    print("Tutor " + name + " did not fill out the availibility poll")
                    break
            elif i % 2 == 0:
                pass # skip over quarter hour availibility
            elif (on_weekend or row[0].startswith("Sunday") or row[0].startswith("Saturday")) and day_beg_skip_count < const_csil_params.BLOCK_SKIP_WEEKEND_MORNING:
                # print("beg_skip", on_weekend, day_beg_skip_count, day_end_skip_count, b)
                on_weekend = True
                day_beg_skip_count += 1
                pass
            elif day_end_skip_count == 0:
                if b >= const_csil_params.BLOCKS_PER_DAY[d]:
                    b = 0
                    d += 1
                    if not skip_fix and row[0].startswith("Saturday"):
                        skip_fix = True
                        avail_val = int(row[tutor_col])
                        # print("day:", d % 7, "block:", b, "avail_val:", int(row[tutor_col]))
                        if avail_val == 0: 
                            conf_pref_sched.state[d][b] = const_csil_params.CONFLICT_TERMS_CODES["Conflict"]
                        b += 1
                    else:
                        if on_weekend:
                            day_end_skip_count = 1
                        else:
                            avail_val = int(row[tutor_col])
                            # print("day:", d % 7, "block:", b, "avail_val:", int(row[tutor_col]))
                            if avail_val == 0: 
                                conf_pref_sched.state[d][b] = const_csil_params.CONFLICT_TERMS_CODES["Conflict"]
                            b += 1
                else:
                    avail_val = int(row[tutor_col])
                    # print("day:", d % 7, "block:", b, "avail_val:", int(row[tutor_col]))
                    if avail_val == 0: 
                        conf_pref_sched.state[d][b] = const_csil_params.CONFLICT_TERMS_CODES["Conflict"]
                    b += 1
            else:
                # print("end_skip", on_weekend, day_beg_skip_count, day_end_skip_count)
                if day_end_skip_count == const_csil_params.BLOCK_SKIP_WEEKEND_NIGHT - 1:
                    day_end_skip_count = 0
                    day_beg_skip_count = 0
                    on_weekend = False
                else:
                    day_end_skip_count += 1
                pass
    return conf_pref_sched

def get_conflicts_indices(state):
    conf_indices = set([])
    for d in range(len(state)):
        for b in range(len(state[d])):
            if state[d][b] == const_csil_params.CONFLICT_TERMS_CODES["Conflict"]:
                conf_indices.add((d, b))
    return conf_indices

def get_available_indices(state):
    available_indices = []
    for d in range(len(state)):
        for b in range(len(state[d])):
            if state[d][b] != const_csil_params.CONFLICT_TERMS_CODES["Conflict"]:
                available_indices.append((d, b))
    return sorted([*set(available_indices)])
    

# given the filepaths of the main google form csv output, and the two when2meets,
# parses the data of all tutors and stores it as CSILTutorsInfo
# This parsing is extremely contingent on the form formatting, but variable names
# are clear so if the form output changes, changing this should be simply
# altering indices.
def csv_to_tutors_info(csv_paths):
    google_form_filepath = csv_paths[0]
    availibility_filepath = csv_paths[1] 
    preferred_filepath = csv_paths[2]
    with open(google_form_filepath, newline='', encoding = 'cp850') as csvfile:
        tutors_info = []
        rd = csv.reader(csvfile)
        next(rd)
        for row in rd:
            for i, _ in enumerate(row):
                row[i] = row[i].strip()
            name = row[2]
            years_worked = const_csil_params.THIS_YEAR - int(row[4])
            teams = [const_csil_params.CSIL_TEAM_CODES[x] for x in row[7].split(", ") if x in const_csil_params.CSIL_TEAMS]
            total_blocks = int(row[6]) * const_csil_params.BLOCKS_PER_HOUR
            shift_len = const_csil_params.SHIFT_LEN_CODES[row[5]]
            desk_mates = row[8].split(", ") # optimized in csil_tutors_info
            conflicts_preferences = generate_conflicts_preferences(name, availibility_filepath, preferred_filepath)
            conflicts_indices = get_conflicts_indices(conflicts_preferences.state)
            available_indices = get_available_indices(conflicts_preferences.state)
            tutors_info.append(tutor_info.TutorInfo(name, years_worked, teams, total_blocks, shift_len, desk_mates, conflicts_preferences, conflicts_indices, available_indices))
            tutors_info.sort(key=lambda x: x.name)
        output = csil_tutors_info.CSILTutorsInfo(tutors_info)
        return output

# print(csv_to_tutors_info(["input_csvs/main.csv", "input_csvs/availibility.csv", "input_csvs/preferred.csv"]))
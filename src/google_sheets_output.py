import const_csil_params
import gspread_formatting as gsf
import gspread

# First parse the weekly schedule state in two parts:
# One is a sheet where each tutor has their own row and the columns are the days of the week,
# each cell contains the number of hours that tutors works that day
#
# Next, the actual schedule is split up by days into separate sheets
# For each day, each block gets one row, with a tutor on shift filling that block's cell
# There can be at most 4 tutors for one block
# Each tutor should have a column segment for when they are on shift for readability
# (continues whatever slot they were first put into)

# Lastly all of this information needs to be sent to a google sheet, written, color-coded, and
# Shared with the appropriate scheduling staff.

# A special gmail account will be created for this bot, with credentials in the password manager


def format_summed_daily_hours(state, csil_tutors_info):
    num_tutors = csil_tutors_info.num_tutors
    tutors_info = csil_tutors_info.tutors_info
    header = ["Name", "Total Hours", "Monday", "Tuesday",
              "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    output = [header]
    for tid in range(num_tutors):
        tutor = tutors_info[tid]
        cur_row = ['' for _ in header]
        cur_row[0] = tutor.name
        total_sum = 0
        day_offset = 2
        for d in state:
            sum = 0
            for b in d:
                if tid in b:
                    sum += 1
            total_sum += sum
            cur_row[day_offset] = sum / const_csil_params.BLOCKS_PER_HOUR
            day_offset += 1
        cur_row[1] = total_sum / const_csil_params.BLOCKS_PER_HOUR
        output.append(cur_row)
    return output


def format_one_days_schedule(state, csil_tutors_info, day):
    header = ["Start Time", "End Time"]
    header_buff = len(header)
    for i in range(const_csil_params.MAX_TUTORS_ON_SHIFT):
        header.append("Tutor " + str(i))

    output = [header]
    tutor_to_col_map = {tid: -1 for tid in range(csil_tutors_info.num_tutors)}
    tutor_pref_col_map = {
        tid: -1 for tid in range(csil_tutors_info.num_tutors)}
    taken_cols = [False for _ in range(const_csil_params.MAX_TUTORS_ON_SHIFT)]
    prev_b = set([])
    for bi, b in enumerate(state[day]):
        cur_row = [""] * (header_buff + const_csil_params.MAX_TUTORS_ON_SHIFT)
        cur_row[0] = const_csil_params.CSIL_START_TIMESTAMPS[day][bi]
        cur_row[1] = const_csil_params.CSIL_END_TIMESTAMPS[day][bi]

        for tid in prev_b:
            if tid not in b:
                taken_cols[tutor_to_col_map[tid]] = False
                tutor_to_col_map[tid] = -1

        for tid in b:
            if tutor_to_col_map[tid] == -1:
                if tutor_pref_col_map[tid] != -1 and not taken_cols[tutor_pref_col_map[tid]]:
                    taken_cols[tutor_pref_col_map[tid]] = True
                    tutor_to_col_map[tid] = tutor_pref_col_map[tid]
                else:
                    i = 0
                    while (i < len(taken_cols) and taken_cols[i]):
                        i += 1
                    if i >= const_csil_params.MAX_TUTORS_ON_SHIFT:
                        print("error: too many tutors scheduled at one time")
                        break
                    taken_cols[i] = True
                    tutor_to_col_map[tid] = i
                    tutor_pref_col_map[tid] = i
            cur_row[header_buff + tutor_to_col_map[tid]
                    ] = csil_tutors_info.tutors_info[tid].name
        prev_b = b
        output.append(cur_row)
    return output


def clear_sheets(ws):
    for w in ws:
        w.clear()
    return


def write_title_sheet(ws, title_sheet, csil_tutors_info):
    w = ws[0]
    w.update(title_sheet)
    rules = gsf.get_conditional_format_rules(w)
    rules.clear()
    for tid in range(csil_tutors_info.num_tutors):
        color_rule = gsf.ConditionalFormatRule(
            ranges=[gsf.GridRange.from_a1_range('A', w)],
            booleanRule=gsf.BooleanRule(
                condition=gsf.BooleanCondition(
                    'TEXT_EQ', [csil_tutors_info.tutors_info[tid].name]),
                format=gsf.CellFormat(backgroundColor=const_csil_params.SHEET_COLORS[tid]
                                      )))
        rules.append(color_rule)
    rules.save()
    return


def write_days_sheets(ws, days_sheets, csil_tutors_info):
    d = 0
    for w, ds in zip(ws[1:], days_sheets):
        # Raw text
        w.update(ds)

        # Add timestamp style
        start_fmt = gsf.cellFormat(backgroundColor=gsf.color(0.75, 0.75, 0.75), textFormat=gsf.textFormat(bold=True))
        end_fmt = gsf.cellFormat(backgroundColor=gsf.color(0.9, 0.9, 0.9))
        num_timestamps = len(const_csil_params.CSIL_START_TIMESTAMPS[d])

        gsf.format_cell_range(w, 'A2:A' + str(num_timestamps + 1), start_fmt)
        gsf.format_cell_range(w, 'B2:B' + str(num_timestamps + 1), end_fmt)


        # Add tutor colors
        rules = gsf.get_conditional_format_rules(w)
        rules.clear()
        for tid in range(csil_tutors_info.num_tutors):
            color_rule = gsf.ConditionalFormatRule(
                ranges=[gsf.GridRange.from_a1_range('C:G', w)], # need to un-hardcode
                booleanRule=gsf.BooleanRule(
                    condition=gsf.BooleanCondition(
                        'TEXT_EQ', [csil_tutors_info.tutors_info[tid].name]),
                    format=gsf.CellFormat(backgroundColor=const_csil_params.SHEET_COLORS[tid]
                                        )))
            rules.append(color_rule)
        rules.save()
        d += 1
    return


def write_state_to_sheet(state, csil_tutors_info):
    title_sheet = format_summed_daily_hours(state, csil_tutors_info)
    days_sheets = [format_one_days_schedule(
        state, csil_tutors_info, d) for d in range(7)]

    # ensure that your gspread api credentials are in keys/service_acount.json
    gc = gspread.service_account(
        filename="keys/service_account.json")
    sh = gc.open("Auto Generated Weekly Tutor Schedule")
    ws = sh.worksheets()

    clear_sheets(ws)
    write_title_sheet(ws, title_sheet, csil_tutors_info)
    write_days_sheets(ws, days_sheets, csil_tutors_info)
    return 0


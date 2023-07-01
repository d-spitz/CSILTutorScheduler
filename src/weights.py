# Defines the weights used in scoring a schedule, can be changed as needed
SCORING_WEIGHTS = {"total_blocks": 4,
                   "shift_len": 40,
                   "desk_mates": 2,
                   "conflicts_preferences": 50,
                   "teammates": 3,
                   "seniority": [1, 1.25, 1.5, 1.75, 2, 2],
                   "min_max_tutors_per_block" : 175}

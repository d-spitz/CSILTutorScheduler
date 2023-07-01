import const_csil_params
# This class stores data for a weekly CSIL schedule
# It is a 2d array where the rows are days and the columns are shift blocks
# The schedule is either global and stores the state for annealing/scheduling all tutors,
# or it can be used for an individual tutor to store shift conflicts/preferences

class Schedule:
    # the state is the 2d array of schedule info
    state = []
    # copy of tutors_info dict for printing
    tutors_info = {}
    # local or global schedule
    is_global = False

    # If constructed with no arguments, it is a local schedule, otherwise global
    # If a local schedule, insert 0's in each cell by default (conf/pref value)
    # If a global schedule, insert empty sets in each cell (tutors assigned to this shift)
    def __init__(self, csil_tutors_info=None):
        self.state = []
        if csil_tutors_info:
            self.is_global = True
            self.tutors_info = csil_tutors_info.tutors_info
        else:
            self.is_global = False
        for d in range(7):
            day_blocks = []
            for _ in range(const_csil_params.BLOCKS_PER_DAY[d]):
                day_blocks.append(set([]) if self.is_global else 0)
            self.state.append(day_blocks)

    # Can be used to output a csv, but ugly
    def __str__(self):
        return str(self.state)

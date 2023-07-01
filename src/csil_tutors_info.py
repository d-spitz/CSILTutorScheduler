# This class stores all data parsed from the scheduling form
# Essentially, it is an dict of TutorInfo entries for each tutor, assigning
# each tutor a unique ID to index by. 
# It also holds some metadata as annotated below

class CSILTutorsInfo:
    # The number of tutors at CSIL
    num_tutors = 0

    # The dict that stores TutorInfo entries by unique ID
    tutors_info = {}

    # A dictionary of all the teams at CSIL with a set of their members' IDs as values
    teams_members = {}

    # A reverse dict mapping of a tutor's name to their ID
    # Assumes all tutors have unique names that are found unaltered across the main.csv input
    names_to_ids = {}

    # This constructor takes an array of already populated TutorInfo entries, and calculates
    # the appropriate metadata
    def __init__(self, list_tutor_info):
        self.num_tutors = len(list_tutor_info)
        self.tutors_info = {}
        self.teams_members = {}
        self.names_to_ids = {}

        # Populates tutors_info, teams_members, and names_to_ids
        for id, t in enumerate(list_tutor_info):
            self.tutors_info[id] = t

            for team in t.teams:
                if team in self.teams_members:
                    self.teams_members[team].add(id)
                else:
                    self.teams_members[team] = set([id])
        for id, t in enumerate(list_tutor_info):
            self.names_to_ids[t.name] = id

        # This just converts desk_mates stored as list(strings) to list(int id), this is 
        # done after, as the id isn't assigned per tutor until this constructor is called.
        # The idea is to save on efficiency and to only work with ints
        for t in list_tutor_info:
            if t.desk_mates == ['']:
                t.desk_mates = []
            t.desk_mates = [self.names_to_ids[m] for m in t.desk_mates if m in self.names_to_ids]

    # Just for debugging, prints out the info stored in this object
    def __str__(self):
        s = ""
        for k, v in self.tutors_info.items():
            s += str(k) + ": " + str(v)
            s += "\n"
        # s += str(self.teams_members)
        return s
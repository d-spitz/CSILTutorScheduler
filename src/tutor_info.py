import schedule

# This class stores the scheduling form data for one tutor
# A lot of the data is encoded to ints, the details can be seen in 
# const_csil_params

class TutorInfo:
    # The tutor's name (preferably up to uniqueness)
    name = ""

    # The number of years they have worked at csil
    years_worked = 0

    # The teams they are apart of, encoded    
    teams = None

    # The total number of shift blocks they want to work
    total_blocks = 0

    # The preferred shift length (shorter/longer), encoded  
    shift_len = 0 

    # Their preferred desk mates, encoded to ids once fully parsed
    desk_mates = None

    # Their encoded conflicts/preferences stored in a schedule object
    conflicts_preferences = schedule.Schedule()

    # A set of their conflict indices in the schedule for ensuring correctness
    conflicts_indices = set([])

    # A list of the available indices in the schedule for ensuring correctness
    available_indices = []

    # Stores all above previously parsed data from the scheduling form output into the respective fields
    def __init__(self, name, years_worked, teams, total_blocks, shift_len, desk_mates, conflicts_preferences, conflicts_indices, available_indices):
        self.name = name
        self.years_worked = years_worked
        self.teams = teams
        self.total_blocks = total_blocks
        self.shift_len = shift_len
        self.desk_mates = desk_mates
        self.conflicts_preferences = conflicts_preferences
        self.conflicts_indices = conflicts_indices
        self.available_indices = available_indices
    
    # Prints all data for testing
    def __str__(self):
        temp_dict = {"name": self.name,
                     "years_worked": self.years_worked,
                     "teams": self.teams,
                     "total_blocks": self.total_blocks,
                     "shift_len": self.shift_len,
                     "desk_mates": self.desk_mates,
                     "conflicts_preferences": str(self.conflicts_preferences),
                     "conflicts_indices": str(sorted(tuple(self.conflicts_indices))),
                     "avail_indices": str(sorted(self.available_indices))}
        return str(temp_dict)

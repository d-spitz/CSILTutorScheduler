import sa
import google_sheets_output as gs
import parse_form_output 
import annealing_params as ap

# Runs the annealing process, right now just prints the outputted schedule but will
# write to google sheets eventually
def main():
    print("Welcome to the Automated Simulated Annealing CSIL Tutor Schedule Generator, ASACTSG for short.")
    print("Please ensure you have followed the instructions in the readme.")
    print()
    # Parse input csv into CSILTutorsInfo
    csv_paths = ["input_csvs/" + i for i in ["main.csv", "availability.csv", "preferred.csv"]]
    # Initialize annealer with CSILTutorsInfo
    print("Parsing input csvs . . . ", end="")
    csil_tutors_info = parse_form_output.csv_to_tutors_info(csv_paths)
    print("success!", "\n")

    print("Initializing annealing process . . . ", end="")
    annealer = sa.ScheduleAnnealer(csil_tutors_info)
    
    # annealing parameters
    annealer.set_schedule(ap.auto_settings)
    print("success!")

    # Run annealing process
    print("Beginning annealing process . . . ")
    state, energy = annealer.anneal()
    print()

    print("Successfully annealed tutor schedule, ending energy =", energy, "\nBeginning to write to google sheet . . . ", end="")

    gs.write_state_to_sheet(state, csil_tutors_info)
    print("success!")

    print()
    print("Thanks! Make sure to thank David Spitz and check on the updated google sheet which should be shared with you.")
    return 

# This is used to find good annealer temperature paramaters
def get_auto_settings():
    # Parse input csv into CSILTutorsInfo
    csv_paths = ["input_csvs/" + i for i in ["main.csv", "availibility.csv", "preferred.csv"]]
    # Initialize annealer with CSILTutorsInfo
    print("Parsing input csvs . . . ", end="")
    csil_tutors_info = parse_form_output.csv_to_tutors_info(csv_paths)
    print("success!", "\n")

    print("Searching for optimal temperatures for annealing . . . ", end="")
    annealer = sa.ScheduleAnnealer(csil_tutors_info)
    
    # auto settings were found with this process
    auto_settings = annealer.auto(minutes=2)
    print("success! Use these settings:")
    print(auto_settings)
    return

if __name__ == "__main__":
    main()
    # get_auto_settings()
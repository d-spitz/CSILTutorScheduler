# Auto-Scheduler with Simulated Annealing
This app takes in tutor scheduling info and will autogenerate a schedule using [simulated annealing](https://en.wikipedia.org/wiki/Simulated_annealing). The goal is to approximate an "optimal" schedule which will provide tutors with the hours they'd like to work as well as weighting various other factors such as team-members being scheduled together, shift lengths, etc., which are all data gathered from a Google form. This should save the scheduling team time so instead of starting from a blank slate, they have a good schedule that would only need some tweaks. All you have to do is feed it the input data, and it will do the rest, guaranteeing correctness (no conflicts and proper amount of time scheduled per tutor, hopefully). The simulated annealing algorithm doesn't find an optimal solution every time, it approximates a solution to the scheduling problem which takes exponential time (provided P != NP). See instructions below for how to use this:

Quick note, this tutorial was meant for internal use at CSIL and assumed the Google Sheets API was set up. If this is used outside of that environment, then follow these steps:
   - Follow the [tutorial here](https://docs.gspread.org/en/latest/oauth2.html#enable-api-access-for-a-project) to create a Google Sheets API project and get the credentials json file
   - Use the `service_account.json` file to replace [`keys/service_account.json`](https://github.com/d-spitz/CSILTutorScheduler/blob/628d9cd36412cf8bcb39f52a16f4077281de4dc9/keys/service_account.json)
   - Create a new Google sheet with the title *Auto Generated Weekly Tutor Schedule* and share it with the Google account that you used to create the API project

## How to run the algorithm
This algorithm uses python3 and pip to install needed packages. It is a good idea to use a python virtual environment for this.

1. Navigate to a directory you want this program in, clone the repo and enter the repo directory
2. Now you have to provide the input .csv files, which are located in `input_csvs`. The following files that are updated must be named *exactly* `main.csv`, `availability.csv`, and `preferred.csv`.
	- The first one is *main.csv*. For this one you should download the Google form responses as a csv file from the Google sheet, then replace the existing main.csv content with this file's content. Ensure each row is a valid entry from the form, and that there are no duplicates.
	- The next two are *availability.csv* and *preferred.csv*, which correspond respectively to the availability and preferred slots when2meet polls. Navigate to each when2meet site, open the JS console with inspect element, and copy/run the scraping code found in `when2meet_scraping/scrape_confpref.js`. Take the terminal csv output, and copy it into the respective file in `input_csvs`.
	- **Important:** you need to ensure these scraped files are parsed correctly. Go through the header (first row in the csv file) and ensure that tutors names line up *exactly* with their names in the Google form. The formula is: first letter in name capitalized, and the rest lowercase, and only first name unless there are two people with that first name, in which case keep last name with same format as first. **Also, duplicates need to be handled.** If a tutor entered data more than once, change their header name in unneeded columns to a dummy name like "dummy". Follow the existing files' example.
3. Now you are ready to run the algorithm. (This will pip install some things as listed in the next script. If you don't want this, install them locally or use virtualenv.) Execute this script to install dependencies and run the algorithm:
	- `bash sa.sh` (you may need to make this executable)
	- You should see terminal output confirming the annealing has started
4. Once the algorithm has finished, it will write all data to [this Google sheet](https://docs.Google.com/spreadSheets/d/16LX0Z_ugOk2yL60qDWnNC1lI7wpbAlarZgeLVsJyGL8/edit?usp=sharing).
	- If you need access to this sheet, ask Cosmos.

## Tweaking parameters to achieve better results

- Annealing parameters can be tweaked in `annealing_params.py`
- The weighting of different factors can be edited in `src/weights.py`.
- Changing overall CSIL rules like minimum number of tutors on shift can be found in `src/const_csil_params.py`
- Of course, the input data can be changed as well, like the number of hours a tutor should work.
- For broad customizability beyond the CSIL form structure, the parsing logic would need to be updated

Thanks! 

## Future work
Future work on this project could include making this into a fully-functional webapp to avoid any manual pasting of files or scraping schedule data. Schedules could be visualized more powerfully than they are in Google Sheets. The algorithm could be easier to customize with sliders relating to weights, or easier comparison of different runs. Lastly the runtime could use improvement by perhaps coding this in a faster language than python.

Credit to [this developer](https://github.com/perrygeo) for implementing the simulated annealing package [simanneal](https://github.com/perrygeo/simanneal) used in this project.

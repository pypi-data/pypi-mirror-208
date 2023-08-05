# A simple task tracking system
import os
import io
import re
import argparse
import datetime
import calendar
import subprocess

from did.colors import Colors

DID_HOME = os.path.expanduser("~/.did")
DID_DATA = f"{DID_HOME}/data"
EDITOR = os.environ.get('EDITOR', 'vim')

def get_date_header(date: datetime.date) -> str:
    week = date.isocalendar()[1]
    return f"# {calendar.day_name[date.weekday()]} {date.day} {calendar.month_name[date.month]} {date.year} - Week {week}" 

def get_copied_file_location(day: datetime.date) -> str:
    return f"{DID_DATA}/{day.year}/{day.isocalendar()[1]}/copied-{day.weekday()}.md"

def get_file_location(day: datetime.date) -> str:
    return f"{DID_DATA}/{day.year}/{day.isocalendar()[1]}/{day.weekday()}.md"

def colorise(line: str) -> str:
    string = ""
    if re.search("^# ", line):
        string += f"{Colors.BOLD}{Colors.CYAN}"
    elif re.search("^- \[ \]", line):
        string += f"{Colors.RED}"
    elif re.search("^- \[X\]", line):
        string += f"{Colors.GREEN}"
    elif re.search("^\s+-", line):
        string += f"{Colors.YELLOW}"

    return string + f"{line[:-1]}{Colors.END}"

def get_did_day_as_string(date: datetime.date) -> str:
    output = ""
    file_location = get_file_location(date)
    copied_file_location = get_copied_file_location(date)
    if (os.path.exists(copied_file_location)):
        file_location = copied_file_location

    if (not os.path.exists(file_location)):
        output = f"You did nothing on {date}\n"
    else:
        with open(file_location) as file:
            for line in file:
                output += colorise(line) + '\n'
    return output

def show_day(date: datetime.date) -> None:
    output = get_did_day_as_string(date)
    echo_out = subprocess.Popen(('echo', output), stdout=subprocess.PIPE)
    subprocess.call(['less', '-R', '-F'], stdin=echo_out.stdout)

def get_did_week_as_string(date: datetime.date) -> str:
    output = ""
    week_path = f"{DID_DATA}/{date.year}/{date.isocalendar()[1]}"
    if (not os.path.exists(week_path)):
        output = f"You did nothing in week {date.isocalendar()[1]}\n"
    else:
        for weekday in range(1,8):
            day = datetime.date.fromisocalendar(date.year, date.isocalendar()[1], weekday)
            output += get_did_day_as_string(day) + '\n'
    return output

def show_week(date: datetime.date) -> None:
    output = get_did_week_as_string(date)
    echo_out = subprocess.Popen(('echo', output), stdout=subprocess.PIPE)
    subprocess.call(['less', '-R', '-F'], stdin=echo_out.stdout)

def get_last_weekday(weekday: int) -> datetime.date:
    one_day = datetime.timedelta(days=1)
    date = datetime.date.today() - one_day
    while (date.weekday() != weekday):
        date = date - one_day
    return date

def handle_date(date: str) -> None:
    today = datetime.date.today()
    if (date == 'today'):
        show_day(today)
    elif (date == 'yesterday' or date == 'yes'):
        show_day(today - datetime.timedelta(days=1))
    elif (date == 'monday' or date == 'mon'):
        show_day(get_last_weekday(0))
    elif (date == 'tueday' or date == 'tue'):
        show_day(get_last_weekday(1))
    elif (date == 'wednesday' or date == 'wed'):
        show_day(get_last_weekday(2))
    elif (date == 'thursday' or date == 'thu'):
        show_day(get_last_weekday(3))
    elif (date == 'friday' or date == 'fri'):
        show_day(get_last_weekday(4))
    elif (date == 'saturday' or date == 'sat'):
        show_day(get_last_weekday(5))
    elif (date == 'sunday' or date == 'sun'):
        show_day(get_last_weekday(6))
    elif (date == 'thisweek' or date == 'week' or date == 'w'):
        show_week(today)
    elif (date == 'lastweek' or date == 'lw'):
        show_week(today - datetime.timedelta(days=7))
    else:
        try:
            day = datetime.date.fromisoformat(date)
            show_day(day)
        except ValueError:
            print(f'Invalid date format: {date}')

def prettify_grep_output(grep_output: str, search: str) -> None:
    matched_dates = {}
    lines = grep_output.splitlines()
    for line in lines:
        filename_match = re.search('(?P<year>[0-9]+)/(?P<week>[0-9]+)/(?:copied-)?(?P<day>[0-6]).md:[0-9]+:', line)
        year = int(filename_match.group('year'))
        week = int(filename_match.group('week'))
        day = int(filename_match.group('day')) + 1 # from iso takes days in 1-7 not 0-6
        date = datetime.date.fromisocalendar(year, week, day)
        text = line[filename_match.span()[1]:]
        search_match = re.search(search, text, re.IGNORECASE)
        search_span = search_match.span()
        colorised_text = text[:search_span[0]] + Colors.RED + text[search_span[0]:search_span[1]] + Colors.END + text[search_span[1]:] 
        if date in matched_dates:
            matched_dates[date].append(colorised_text)
        else:
            matched_dates[date] = [colorised_text]

    output = ""
    for date in sorted(matched_dates, reverse=True):
        output += Colors.CYAN + get_date_header(date) + Colors.END + "\n"
        for match in matched_dates[date]:
            output += match + '\n'
        output += '\n'
    echo_out = subprocess.Popen(('echo', output), stdout=subprocess.PIPE)
    subprocess.call(['less', '-R', '-F'], stdin=echo_out.stdout)

def handle_search(search: str) -> None:
    output = subprocess.run(['grep', '--color=auto', '-rni', search, DID_DATA], stdout=subprocess.PIPE).stdout.decode('utf-8')
    if len(output) == 0:
        return
    prettify_grep_output(output, search)

# Copy recent unfinished tasks to todays file if they aren't already present
# If today is the first entry in this week, look at the previous week
# Otherwise look through the previous files from this week
def copy_unfinished_tasks_to_file(file: io.TextIOWrapper, today: datetime.date) -> None:
    copy_week = f"{DID_DATA}/{today.year}/{today.isocalendar()[1]}"
    if (len(os.listdir(copy_week)) == 1): # if we are making the first file of the week
        last_week = today - datetime.timedelta(days=7)
        copy_week = f"{DID_DATA}/{today.year}/{last_week.isocalendar()[1]}"
    for filename in os.scandir(copy_week):
        if filename.is_file() and str(today.weekday()) not in filename.name and re.search("^[0-6].md", filename.name):
            with open(filename.path, 'r') as copy_file:
                first_line = True
                copy_notes = False
                completed_task = False
                for line in copy_file:
                    if first_line:
                        first_line = False
                        continue
                        
                    if not completed_task and copy_notes and re.search("^\s+-", line):
                        file.write(line)
                    elif re.search("^- \[ \]", line):
                        copy_notes = True
                        completed_task = False
                        file.write(line)
                    elif re.search("^- \[X\]", line): # A completed task
                        copy_notes = False
                        completed_task = True
                    else: # Any other line type
                        file.write(line)
                        completed_task = False
                        copy_notes = False
            os.rename(filename.path, f"{copy_week}/copied-{filename.name}")

def did() -> None:
    today = datetime.date.today()
    week = today.isocalendar()[1]
    today_file = f"{DID_DATA}/{today.year}/{week}/{today.weekday()}.md"
    today_header = get_date_header(today)

    if (not os.path.exists(today_file)):
        os.makedirs(f"{DID_DATA}/{today.year}/{week}", exist_ok=True) # make the dirs if they don't exist
        with open(today_file, 'w') as file:
            file.write(f"{today_header}\n")
            copy_unfinished_tasks_to_file(file, today)

    # Open the editor
    subprocess.call([EDITOR, "+ normal GA", today_file])

def handle_args(args: argparse.Namespace) -> None:
    if (args.date):
        handle_date(args.date)
    elif (args.search):
        handle_search(args.search)
    else:
        did()

def initialise() -> None:
    if (not os.path.exists(DID_HOME)):
        print("did home directory does not exist. creating {DID_HOME}")
        os.makedirs(DID_HOME)

def main() -> None:
    initialise()
    parser = argparse.ArgumentParser(
                    prog = 'did',
                    description = 'what did i do?')
    parser.add_argument('date', nargs='?', help='open the did file for this date (try "monday", "thisweek", "lastweek" or "yesterday"!)')
    parser.add_argument('-s', '--search', required=False, help='search for text in did files')
    args = parser.parse_args()
    handle_args(args)

if __name__ == '__main__':
    main()

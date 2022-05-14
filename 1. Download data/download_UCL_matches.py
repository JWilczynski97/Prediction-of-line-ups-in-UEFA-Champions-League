# Copyright (c) Jakub Wilczyński 2020
# The task of this program is getting data about squads in all UEFA Champions League matches of the seasons
# from 2010/2011 to 2019/2020. The script downloads the webpages from WhoScored.com. These websites include
# the information about starting line-ups and predicted line-ups for UEFA Champions League matches.
# The html codes of these websites are saved to the html files on the local disk in specified folder.
# In the next step the script saves into the local SQLite database into table "UCL_Matches" such information about the UCL matches:
# index, team home, team away, season, WhoScored id of match, date, path to file with "Centre", path to file with "Preview", link to the website "Centre".
# Data about teams are saved into table "Team": Whoscored id of team, team name, league (country), link to webpage.
# Data are saving into the database after downloading of all websites - it isn't optimal solution, probably today I would use 'multiprocessing' module.
# Tools used: Python 3.8.2, Selenium Webdriver 3.141.0, BeautifulSoup  4.9.1, SQLite 3.28.0.

from Tools.tools import Database, Logger
from time import sleep
from os import makedirs, getcwd
from random import uniform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from selenium.common.exceptions import NoSuchElementException
from os import listdir, path
from bs4 import BeautifulSoup
import sqlite3 as lite
import logging
import datetime

# important structures
ALL_SEASONS = ['2010/2011', '2011/2012', '2012/2013', '2013/2014', '2014/2015', '2015/2016', '2016/2017', '2017/2018', '2018/2019', '2019/2020']
number_of_downloaded_matches = 0  # it helps to number the downloaded files
MATCHES_FOLDER = 'Matches'
MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
          "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
DATABASE = 'Matches_DB.db'
DRIVER_PATH = "../Tools/chromedriver.exe"

# web driver options
options = Options()
options.add_argument('start-maximized')  # maximize of the browser window
options.add_experimental_option("excludeSwitches", ['enable-automation'])  # process without information about the automatic test
options.add_argument("chrome.switches")
options.add_argument("--disable-extensions")
browser = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)


# functions
def create_directory_for_files(folder):
    """This function creates directory (if doesn't exist) for the files included downloaded websites.\n
    :param folder: str, name of folder coming from current season name"""
    if not path.exists(getcwd() + folder):
        makedirs(getcwd() + folder)
        log.write(f"Directory {folder} created.")


def cookies_accept():
    """Clicking the 'cookies accept' buttons on the start page"""
    more_options_cookies_button = browser.find_element_by_xpath('//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]')
    more_options_cookies_button.click()
    sleep(uniform(3, 5))  # time sleep generator


def is_element_clickable(element):
    """If the element isn't clickable, the current page waits next 5-7 seconds.\n
    :param element: Element, the element from the current page"""
    if not element_to_be_clickable(element):
        log.write("The element is not yet clickable. Waiting...")
        sleep(uniform(5, 7))
    if not element_to_be_clickable(element):
        raise Exception("Unexpected error! The element is not clickable. The end of program.")


def select_season(selected_season):
    """This function selects the correct season from "ALL_SEASONS" in the drop down menu on the start page.\n
    :param selected_season: str, name of options in drop down menu 'season' """
    drop_down_menu = browser.find_element_by_name("seasons")
    is_element_clickable(drop_down_menu)
    all_options = drop_down_menu.find_elements_by_tag_name("option")
    is_element_clickable(all_options)

    for option in all_options:
        if option.get_attribute("text") == selected_season:
            drop_down_menu.click()
            sleep(uniform(1.5, 2.5))
            option.click()
            log.write(f"Option {selected_season} selected.")
            sleep(uniform(1.5, 2.5))
            break


def select_stage(stage):
    """This function selects and runs the website with games of the interesting stage."""
    menu = browser.find_element_by_name("stages")
    all_options = menu.find_elements_by_tag_name("option")
    is_element_clickable(menu)
    is_element_clickable(all_options)
    for option in all_options:
        if str(option.get_attribute("text")) == stage or str(option.get_attribute("text")) == "UEFA " + stage:
            menu.click()
            sleep(uniform(1.5, 2.5))
            option.click()
            log.write(f"Option {stage} selected.")
            sleep(uniform(1.5, 2.5))
            break

    # the all matches of stage are located in the Fixtures subpage
    fixtures_button = browser.find_element_by_link_text("Fixtures")
    is_element_clickable(fixtures_button)
    fixtures_button.click()
    sleep(uniform(3, 4))


def download_match():
    """The match downloading function starts in "Match Center" section of the match website, then comes to the Preview."""
    is_preview = False
    sleep(uniform(25, 30))
    html_code = browser.page_source
    save_file(is_preview, html_code)  # saving the website with line-up
    preview_button = browser.find_element_by_link_text("Preview")
    is_element_clickable(preview_button)
    preview_button.click()
    is_preview = True
    sleep(uniform(10, 12))
    html_code_preview = browser.page_source
    save_file(is_preview, html_code_preview)  # saving the website with preview
    print(browser.title[:-19])
    sleep(uniform(4, 5))


def download_websites():
    """The match websites downloading from Group or Final Stage website."""
    matches = browser.find_elements_by_xpath('//*[@id="tournament-fixture"]/div/div/div[8]/a')
    links = []
    print('Matches: ' + str(len(matches)))
    for match in matches:  # it saves the links from 'href' parameters of website elements into the list
        one_link = match.get_attribute("href")
        links.append(one_link)
    sleep(uniform(1.5, 2.5))
    for link_to_match in links:  # it opens every link to the match website and downloads html code
        browser.execute_script(
            "window.open('');")  # execute_script(script, *args) -> this function synchronously executes JavaScript in the current window/frame.
        browser.switch_to.window(browser.window_handles[1])
        browser.get(link_to_match)
        sleep(uniform(4, 5))
        match_centre_button = browser.find_element_by_link_text("Match Centre")
        is_element_clickable(match_centre_button)
        match_centre_button.click()
        sleep(uniform(4, 5))
        try:
            browser.find_element_by_link_text("Preview")
        except NoSuchElementException:
            browser.close()
            sleep(uniform(2, 3))
            browser.switch_to.window(browser.window_handles[0])
            continue
        download_match()
        browser.close()
        sleep(uniform(2, 3))
        browser.switch_to.window(browser.window_handles[0])
        sleep(uniform(2, 3))


def save_file(is_preview, html_code):
    """This function saves the html file with squad.\n
    :param is_preview: bool, defines that currant website contains preview squad or not
    :param html_code: str, contains html code od current downloaded website. """
    global number_of_downloaded_matches, directory
    if not is_preview:
        with open(f"{directory}\\Match_{str(number_of_downloaded_matches + 1)}_squad.html", 'w',
                encoding="utf-8") as f:
            f.write(str(html_code))
    else:
        with open(f"{directory}\\Match_{str(number_of_downloaded_matches + 1)}_preview.html", 'w',
                encoding="utf-8") as f:
            f.write(str(html_code))
            number_of_downloaded_matches += 1
    log.write(f"File {f.name} saved.")


def matches_indexes(ucl_season: str) -> [int]:
    """This function returns indexes of matches from given season.\n
        :param ucl_season: str, name of UEFA Champions League season"""
    squads_files = list(filter(lambda x: 'squad' in x, listdir(f"Matches\\{ucl_season.replace('/', '_')}")))
    ids = [int(x.split("_")[1]) for x in squads_files]
    return sorted(ids)


def get_link_and_id(html_file: str) -> (str, str):
    """ This function returns link to webpage with match centre and WhoScored ID of the given match
        in form od two-element tuple. \n
        :param html_file: str, path to the file with match centre"""
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        whoscored_link = soup.find("link", rel="canonical").get("href")
        match_id = whoscored_link.split("/")[4]
        return whoscored_link, match_id


def get_teams(html_file: str) -> {str}:
    """This function returns WhoScored IDs, names and leagues of both teams in shape of dictionary.
    Keys of the resulting dictionary: 'team1_name', 'team2_name', 'team1_id', 'team2_id',
    'team1_league', 'team2_league'. \n
        :param html_file: str, path to the file with match centre"""
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        teams_names = soup.find("div", id="match-header").find_all("a", class_="team-link")
        teams_ids = soup.find_all("div", class_="pitch-field")
        results = {"team1_name": teams_names[0].string, "team2_name": teams_names[1].string,
                   "team1_id": teams_ids[0].get("data-team-id"), "team2_id": teams_ids[1].get("data-team-id"),
                   "team1_league": teams_names[0].get("href").split("/")[-1].split("-")[0],
                   "team2_league": teams_names[1].get("href").split("/")[-1].split("-")[0]}
        return results


def get_paths(html_file: str) -> (str, str):
    """ This function returns paths to the match centre and preview files for given match. \n
        :param html_file: str, path to the file with match centre"""
    return path.relpath(html_file), path.relpath(html_file.replace("squad", "preview"))


def get_date(html_file: str) -> str:
    """This function returns date of match in the format yyyy-mm-dd. \n
        :param html_file: str, path to the file with match centre"""
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        game_date = soup.find_all("div", class_="info-block cleared")[2].find_all("dd")[1].string[5:]
        assert len(game_date) == 9
        day, month, year = game_date.split("-")
        game_date = datetime.date(int("20" + year), MONTHS[month], int(day))
        return str(game_date)


def get_season(html_file: str) -> str:
    """This function returns name of UCL season for the given match. \n
        :param html_file: str, path to the file with match centre"""
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        this_season = soup.find("title").string.strip().split(" ")[-2]
        return this_season


def change_team_name(team_id, team_name):
    """This function changes tha names of few clubs.
    The correct names are very importent for the next step of project.\n
    :param team_id: str, WhoScored id of team
    :param team_name: str, WhoScored id of team"""
    change_names = {'32': 'Manchester United', '167': 'Manchester City', '7614': 'Leipzig',
                    '134': 'Borussia M Gladbach',
                    '296': 'Sporting CP', '560': 'Zenit St Petersburg', '304': 'Paris Saint Germain'}
    if team_id in change_names:
        return change_names[team_id]
    return team_name


# 1. downloading of websites
log = Logger(log_folder=None, std_output=True)
log.write("Start of UCL matches downloading.")
browser.get(
    "https://www.whoscored.com/Regions/250/Tournaments/12/Europe-Champions-League")  # Program starts from this website
sleep(uniform(8, 10))
cookies_accept()
for current_season in ALL_SEASONS:  # all UEFA Champions League matches from all seasons are downloaded
    season = current_season.replace("/", "_")  # name of directory can't include "/"
    directory = f"{MATCHES_FOLDER}\\{season}"
    create_directory_for_files(directory)
    select_season(current_season)
    select_stage("Champions League Group Stages")
    download_websites()
    select_stage("Champions League Final Stage")
    download_websites()
    print("Downloading season " + current_season + " complete.")
    sleep(uniform(8, 10))
    log.write(f"Matches from season {season} downloaded.")
browser.close()
log.write("Closing the browser.")
log.write("The End of downloading. All html files saved.")


# 2. saving data to the database
db = Database(DATABASE, log)
try:
    for season in ALL_SEASONS:
        for idx in matches_indexes(season):  # for every saved UCL match

            # downloading data from html files
            file = f"{MATCHES_FOLDER}/{season.replace('/', '_')}/Match_{idx}_squad.html"
            link, whoscored_id = get_link_and_id(file)
            paths = get_paths(file)
            match_date = get_date(file)
            teams = get_teams(file)
            teams["team1_name"] = change_team_name(teams["team1_id"], teams["team1_name"])
            teams["team2_name"] = change_team_name(teams["team2_id"], teams["team2_name"])
            season = get_season(file)
            link_team_1 = f"whoscored.com/Teams/{teams['team1_id']}"
            link_team_2 = f"whoscored.com/Teams/{teams['team2_id']}"

            # adding UCL match to the database
            row = (idx, teams["team1_id"], teams["team2_id"], season, whoscored_id, match_date, paths[0], paths[1], link)
            log.write(f"Data downloaded from file {file}.")
            db.insert('UCL_Matches', False, *row)
            log.write(f"Match with ID {whoscored_id} saved in the database.")

            # adding team to the database if not exists
            if not db.is_element_in_db("Teams", Team_ID=teams["team1_id"]):
                db.insert('Teams', False, teams["team1_id"], teams["team1_name"], teams["team1_league"], link_team_1)
                log.write(f"Team with ID {teams['team1_id']} saved in the database.")

            if not db.is_element_in_db("Teams", Team_ID=teams["team2_id"]):
                db.insert('Teams', False, teams["team2_id"], teams["team2_name"], teams["team2_league"], link_team_2)
                log.write(f"Team with ID {teams['team2_id']} saved in the database.")

            db.commit()
            log.write(f"Changes in the database {DATABASE} saved.")
            log.write(f"File {file} complete.")
except lite.Error as e:
    if db:
        db.rollback()
    log.write(f"SQLite ERROR: {e}", level=logging.ERROR)
except Exception as e:
    if db:
        db.rollback()
    log.write(f"ERROR: {e}")
else:
    db.commit()
    log.write(f"All changes in the database {DATABASE} saved.")

""" ratiba core module """

import requests
from bs4 import BeautifulSoup
import json
from udomratibaapi import utils

def get_semesters(academic_year):
    """ get semester options for the current academic year """
    # get data from udom servers
    url = f"https://ratiba.udom.ac.tz/index.php/downloads/fetch-semesters?year={academic_year['id']}"
    html_text = utils.fetch_data(url)

    # parse the resulting HTML
    soup = BeautifulSoup(html_text, 'html.parser')
    options = soup.find_all('option')[1:] # remove the first option

    semesters = []
    for option in options:
        semesters.append({
            "id": option['value'],
            "text": option.text
        })

    return semesters

def get_categories(academic_year, semester):
    """ get category options for the current academic year and semester """
    # get data from udom servers
    url = f"https://ratiba.udom.ac.tz/index.php/downloads/fetch-categories?year={academic_year['id']}&semester={semester['id']}"
    html_text = utils.fetch_data(url)

    # parse the resulting HTML
    soup = BeautifulSoup(html_text, 'html.parser')
    options = soup.find_all('option')[1:] # remove the first option

    categories = []
    for option in options:
        categories.append({
            "id": option['value'],
            "text": option.text
        })

    return categories

def get_download_options(academic_year, semester, category):
    """ get download options for the current academic year, semester and category """
    # get data from udom servers
    url = f"https://ratiba.udom.ac.tz/index.php/downloads/opt?year={academic_year['id']}&semester={semester['id']}&type={category['id']}"
    html_text = utils.fetch_data(url)

    # parse the resulting HTML
    soup = BeautifulSoup(html_text, 'html.parser')
    options = soup.find_all('option')[1:] # remove the first option

    download_options = []
    for option in options:
        download_options.append({
            "id": option['value'],
            "text": option.text
        })

    return download_options

def get_data(academic_year, semester, category, option):
    """ get data for the current academic year, semester, category and option """
    # get data from udom servers
    url = f"https://ratiba.udom.ac.tz/index.php/downloads/data?year={academic_year['id']}&semester={semester['id']}&type={category['id']}&option={option['id']}"
    html_text = utils.fetch_data(url)

    data = []

    # parse the resulting HTML
    soup = BeautifulSoup(html_text, 'html.parser')
    options = soup.select('#data option')[1:] # remove the first option
    for option in options:
        value = option['value']
        text = option.text.strip()
        data.append({
            "id": value,
            "text": text
        })

    return data

def get_timetable(academic_year, semester, category, option, data):
  ''' Get timetable for a given data choice '''
  # get data from udom servers
  url = f"https://ratiba.udom.ac.tz/index.php/downloads/view?year={academic_year['id']}&semester={semester['id']}&type={category['id']}&option={option['id']}&data[]={data['id']}"
  html_text = utils.fetch_data(url)

  # parse the resulting HTML
  soup = BeautifulSoup(html_text, 'html.parser')
  table = soup.find('table', {'class': 'table'})
  rows = [[td.text.strip() for td in tr.find_all('td')] for tr in table.find_all('tr') if tr.find_all('td')]

  ratiba = []
  days = {}
  sessions = []
  prev_day = rows[0][0]

  # create a custom json object i can work with
  for index, row in enumerate(rows):
    if str(row[0]) != '' and index != 0:
        days["day"] = prev_day
        days["sessions"] = sessions
        prev_day = row[0]

        if index < len(rows)-1:
            ratiba.append(days)
            sessions = []
            days = {}

    if str(row[1]) == "":
        time = str(prev_time)
    else:
        time = str(row[1])
        prev_time = row[1]

    start_time = time.split("-")[0].strip()
    end_time = time.split("-")[1].strip()

    sessions.append({
        "start_time": start_time,
        "end_time": end_time,
        "course": row[2].split("-")[0].strip(),
        "session_type": row[2].split("-")[1].strip(), # "Lecture", "Practical" or "Tutorial"
        "venue": row[3],
        "instructor": row[4],
        "students": [student.strip() for student in row[5].split(",")]
    })

    if index == len(rows)-1:
        days["day"] = prev_day
        days["sessions"] = sessions
        ratiba.append(days)

  return ratiba

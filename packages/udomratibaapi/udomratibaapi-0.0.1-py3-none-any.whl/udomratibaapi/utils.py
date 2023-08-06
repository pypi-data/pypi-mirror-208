""" utility functions """

import requests
from bs4 import BeautifulSoup

def fetch_data(url:str):
  """ fetch data from a given url with correct expeption handling"""
  try:
    response = requests.get(url)
    return response.text
  except requests.exceptions.ConnectionError:
    print("Connection Error")
    return None

def get_current_academic_year():
  """ returns the current academic year (id and text) from scrapping the ratiba website """
  # Send a GET request to the URL and retrieve the HTML content
  html_content = fetch_data("https://ratiba.udom.ac.tz/index.php/downloads/index")

  # Create a BeautifulSoup object to parse the HTML
  soup = BeautifulSoup(html_content, 'html.parser')

  # Find the <select> element with name="year" and id="year"
  select_element = soup.find('select', {'name': 'year', 'id': 'year'})

  # Find all <option> elements within the <select> element
  options = select_element.find_all('option')

  return {"id": options[1]['value'], "text": options[1].text}

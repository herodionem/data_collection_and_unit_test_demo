import os
import requests
import pandas as pd
import logging
from bs4 import BeautifulSoup as bs


logging.basicConfig(level=logging.DEBUG, filename='school_data.log', filemode='w', format='[%(asctime)s] %(levelname)s: %(message)s')


class CollegeFinder():

  def __init__(self, state: str):
    self.state = state.lower()
    self.log = logging
    self._schools = None
    self._smap = None
    self._domain = "https://www.collegesimply.com"

  @property
  def schools(self):
    return self._schools or 'None acquired yet.'

  def initialize(self):
    map = requests.get(f"{self._domain}/colleges/{self.state}/").content
    return bs(map)

  def get_population(self, divs):
    for div in divs:
      if div.get_text().strip().lower() == 'Student Population'.lower():
        num = div.findNext().get_text().strip().replace(',','')
        return 0 if num == '' else int(num)

  def get_schools(self, count=None):

    if not self._smap:
      self._smap = self.initialize()

    if not self._schools:
      self._schools = dict()

    for url in [i.get_attribute_list('href')[0] for i in self._smap.find_all('a') \
      if len(i.get_attribute_list('href')) == 1 \
        and f'/colleges/{self.state}/' in i.get_attribute_list('href')[0] \
        and f'/colleges/{self.state}/' != i.get_attribute_list('href')[0] \
          ]:

      if url.count('colleges') > 1:
        continue

      try:
        result = requests.get(self._domain + url).content
        soup = bs(result)

        try:
          school_url = self._domain + url
        except:
          self.log.exception(f"Could not find a parent link: {soup.find_all('i', {'class':'fa-external-link'})}")

        try:
          population = self.get_population(soup.find_all(class_='card-title'))
        except:
          self.log.exception(f'Problem getting population: {url}')
          input()

        self._schools[url] = [school_url, population]
      except Exception as e:
        self.log.exception(f'{url}')
      if len(self._schools) >= count:
        self.log.info(f'{count} schools requested. Quota met. Ending search...')
        break

  def export(self, filename: str):
    # Woefully insufficient if you are serious about writing a valid, writeable file that
    # won't overwrite an existing file, (esp. if you are on Windows) but this is just a
    # demo. See below for an enjoyable (but lengthy) explication of the matter:
    #   https://stackoverflow.com/questions/9532499/check-whether-a-path-is-valid-in-python-without-creating-a-file-at-the-paths-ta
    if os.path.splitext(filename)[1] != '.csv':
      self.log.warning('I refuse to write anything but csv here... :P')
      return False
    elif not self._schools or len(self._schools) == 0:
      self.log.warning('I am disinclined to acquiesce to your request. (There is nothing here...)')
      return False
    else:
      self.log.info(f'Writing data for {len(self._schools)} schools to file `{filename}`')
      df = pd.DataFrame.from_dict(self._schools, orient='index', columns=['school_home_page', 'population'])
      df.to_csv(filename, index=False, header=True)

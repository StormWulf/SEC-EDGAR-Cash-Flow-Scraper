import logging
import pandas as pd
import re
import requests
import urllib
from bs4 import BeautifulSoup

url = 'https://www.sec.gov/cgi-bin/browse-edgar'


class Company:
    def __init__(self, ticker):
        """
        :param str ticker: Company ticker symbol to search from SEC's EDGAR Company Filings database
        """
        self.ticker = ticker.strip()
        self.cik = None
        self._filings = []
        self._forms = {}

    @property
    def filings(self):
        """
        All of the 10-K filings found for the company
        """
        if not self._filings:
            # params
            params = {
                'action': 'getcompany',
                'CIK': self.ticker,
                'type': '10-k',
                'owner': 'exclude',
                'output': 'atom',
                'count': 100
            }

            # define response
            response = requests.get(url=url, params=params)
            soup = BeautifulSoup(response.content, 'lxml')

            # record numerical CIK
            self.cik = int(re.findall(r'>(.*?)<', str(soup.find('cik')))[0])

            # populate filings
            self._filings = [re.findall(r'>(.*?)<', str(f))[0]
                             for f in soup.find_all('xbrl_href')]
        return self._filings

    @property
    def forms(self):
        """
        The 10-K form found for each filing as a pandas DataFrame
        """
        if not self._forms:
            for filing in self.filings:
                # find SEC Accession Number for filing
                sec_num = re.findall(r'accession_number=(.*?)&', filing)[0]
                sec_int = sec_num.replace('-', '')

                # read excel document for data
                report = f'http://www.sec.gov/Archives/edgar/data/{self.cik}/{sec_int}/Financial_Report.xlsx'
                try:
                    sheets = pd.read_excel(
                        report, sheet_name=None, header=1
                    )
                except:
                    try:
                        # try using .xls extension instead of .xlsx
                        sheets = pd.read_excel(report.replace(
                            'xlsx', 'xls'
                        ), sheet_name=None, header=1)
                    except:
                        logging.error('Excel file was corrupted, skipping')
                        continue

                # find the excel sheet with the Cash Flow data
                # some of the excel sheets have it spelt only as "CAS", so this seems to work
                sheet_name = [
                    sheet for sheet in sheets if 'CAS' in sheet.upper()
                ][0]

                # drop columns that may have junk like footnotes, then drop headers from the table data
                self._forms[sec_num] = sheets[sheet_name].dropna(
                    axis='columns', thresh=10).dropna(thresh=3)

                # track column names in another column so that the models can have consistent field names
                self._forms[sec_num]['period_1_name'] = self._forms[sec_num].columns[1]
                self._forms[sec_num]['period_2_name'] = self._forms[sec_num].columns[2]
                self._forms[sec_num]['period_3_name'] = self._forms[sec_num].columns[3]

                # enforce the expected column names when used to instantiate a Report model
                self._forms[sec_num].columns = [
                    'field', 'period_1', 'period_2', 'period_3', 'period_1_name', 'period_2_name', 'period_3_name'
                ]
        return self._forms

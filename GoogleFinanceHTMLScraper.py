#!/usr/bin/python 

import collections
import requests 
import re 
from bs4 import BeautifulSoup

# Lookup the exchange symbol is listed on and set the exchange in the companies dictionary

def g_scrape_exchange(symbol,d):
  prefix = "http://www.google.com/finance?q="
  postfix = "&ei=HSzqVLKEI6nJiQLG44C4Bw"
  query = prefix + symbol + postfix
  response = requests.get(query)
  soup = BeautifulSoup(response.text)
  title = soup.find("title").find(text=True).strip()
  match = re.search('NASDAQ',title)
  if match: 
    d["exh"] = "NASDAQ"
  match = re.search('NYSE',title)
  if match:
    d["exh"] = "NYSE"

def g_scrape_income_statement(symbol):
  company = dict()
  g_scrape_exchange(symbol,company)
  exchange = company["exh"]
  
  company['symbol'] = symbol
  company['revenue'] = collections.OrderedDict()
  company['net_income'] = collections.OrderedDict()
  company['gross_profit'] = collections.OrderedDict()
  company['operating_income'] = collections.OrderedDict()
  
  prefix = "http://www.google.com/finance?q="
  middle = "%3A"
  postfix = "&fstype=ii&ei=4_vvVLHVCOiniAKAlYDgCA"
  query = prefix + exchange + middle + symbol + postfix
  response = requests.get(query)
  soup = BeautifulSoup(response.text)
  tables = soup.findAll("table", {"class" : "gf-table rgt"})
  
  fields = dict()
  fields = {
    "Net Income":"net_income",
    "Gross Profit":"gross_profit",
    "Revenue":"revenue",
    "Operating Income":"operating_income",
  }
  years = {1:"2014",2:"2013",3:"2012",4:"2011"}
  for table in tables:
    for row in table.findAll("tr"):
      cells = row.findAll("td")
      if len(cells):
        head = cells[0].find(text=True).strip()
        if head in fields:
          for i in range(1,5):
            key = fields[head]
            company[key][years[i]] = float(cells[i].find(text=True).strip().replace(",",""))
  return company

def g_scrape_cash_flow(symbol):
  company = dict()
  g_scrape_exchange(symbol,company)
  exchange = company["exh"]
  if "exh" not in company:
    return None
  
  company['symbol'] = symbol
  company['net_income'] = collections.OrderedDict()
  company['div_paid'] = collections.OrderedDict()
  
  prefix = "http://www.google.com/finance?q="
  middle = "%3A"
  postfix = "&fstype=ii&ei=3Kr8VJGVE8OoiQK6hoCADw"
  query = prefix + exchange + middle + symbol + postfix
  response = requests.get(query)
  soup = BeautifulSoup(response.text)
  tables = soup.findAll("table", {"class" : "gf-table rgt"})
  
  fields = dict()
  fields = {
    "Net Income/Starting Line":"net_income",
    "Total Cash Dividends Paid":"div_paid",
  }
  years = {1:"2014",2:"2013",3:"2012",4:"2011"}
  for table in tables:
    for row in table.findAll("tr"):
      cells = row.findAll("td")
      if len(cells):
        head = cells[0].find(text=True).strip()
        if head in fields:
          for i in range(1,5):
            key = fields[head]
            field = float(cells[i].find(text=True).strip().replace(",","").replace("-",""))
            if field:
              company[key][years[i]] = field 
  return company

def get_sp_500_list():
  wiki = requests.get("http://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
  soup = BeautifulSoup(wiki.text)
  table = soup.find("table", {"class" : "wikitable sortable"})
  sp_500 = list()
  for row in table.findAll("tr"):
    cells = row.findAll("td")
    if len(cells) == 8:
      sp_500.append(cells[0].find(text=True))
  return sp_500

if __name__ == "__main__":
  csco_cash_flow = g_scrape_cash_flow("csco")
  print "===CSCO Net Income==="
  for k,v in csco_cash_flow["net_income"].items():
    print k,v
  print "===CSCO Dividends Paid==="
  for k,v in csco_cash_flow["div_paid"].items():
    print k,v
  sp_500_idx = get_sp_500_list()
  print sp_500_idx[0:10]
  print len(sp_500_idx)


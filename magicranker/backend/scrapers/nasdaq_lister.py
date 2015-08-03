import csv
import re
from StringIO import StringIO

import utils

def get_exchange_url(exchange):
    '''
    Helper to get a url for a list of stocks given an exchange
    '''
    return ("http://www.nasdaq.com/screening/companies-by-industry.aspx?"
                "exchange={}&render=download".format(exchange))


def get_stock_list(exchange):
    stock_list = []
    url = get_exchange_url(exchange)
    csv_page = utils.get_page(url)
    if csv_page:
        csvfile = csv.reader(StringIO(csv_page), delimiter=',')
        for row in csvfile:
            print row
            #Skip rows without data
            if len(row) <= 1:
                continue
            symbol = row[0]
            #Look for all-caps symbols, ignore other characters.
            if re.search(r'^[A-Z]*$', symbol):
                stock_list.append(symbol)
    return stock_list

if __name__ == "__main__":
    #Test nyse
    print get_stock_list("nyse")[:5]


"""
This class reads in multiple json datasets of a similar nature, arrays, and munges them together into
one single large json array for further processing.
"""

import json
import glob
import errno

# for cleanup of cash entries
# (?:")([\w\s\n]+)?(Cash|Credit Card|Check)(\n[\w\s]+)+

def getSites(data):
    sites = []
    for k, v in data.iteritems():
        for e in v:
            if (e.has_key("website")):
                if (e.has_key("email")):
                    payload = {'website': e["website"], 'email': e["email"]}
                else:
                    payload = {'website': e["website"], 'email': 'NULL'}
            else:
                payload = None
            if (payload is not None):
                sites.append(payload)
    return(sites)

def mungeResults(data):
    for movers, values in data.iteritems():
        out = []
        for company in values:
            out.append(company)
    return(out)


def getData():
    """
    Pulls in multiple datasets, all in same json format.
    :return: siteJSON - json object of all urls needing to be visited to extract an email.
    :return: resultlist - json array of json objects, one per record for ETL.
    """
    path = '../data/input/run_results-61.json'
    files = glob.glob(path)
    sitelist = []
    resultlist = []
    for name in files:
        try:
            with open(name) as json_file:
                json_data = json.load(json_file)
                sitelist.extend(getSites(json_data))
                resultlist.extend(mungeResults(json_data))
        except IOError as exc:
            if exc.errno != errno.EISDIR:
                raise  # Propagate other kinds of IOError.
    # this makes the result set comprised of only unique elements
    result = {each['website']: each for each in sitelist}.values()
    # build an array of all urls that need to be visited in secondary extraction
    siteJSON = {"urls": result}
    return(siteJSON, resultlist)

def main():
    siteJSON, resultlist = getData()
    print(resultlist)
    print(len(resultlist))
    result = {each['name']: each for each in resultlist}.values()
    print(result)
    print(len(result))
    with open("../data/output/fetch_emails-2.json", 'w') as fh:
        json.dump(siteJSON, fh)
    with open("../data/output/results-2.json", 'w') as fh:
        json.dump(result, fh)

if __name__ == '__main__':









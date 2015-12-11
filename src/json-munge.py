import json
import re
import glob
import errno

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


def remove_duplicates(values):
    output = []
    seen = set()
    for value in values:
        # If value has not been encountered yet,
        # ... add it to both list and set.
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output

def mungeResults(data):
    return(resultJSON)


path = '../data/input/run_results-*.json'
files = glob.glob(path)
sitelist = []
resultJSON = {}
for name in files:
    try:
        with open(name) as json_file:
            json_data = json.load(json_file)
            sitelist.extend(getSites(json_data))
    except IOError as exc:
        if exc.errno != errno.EISDIR:
            raise  # Propagate other kinds of IOError.

print(len(sitelist))
print(sitelist)
result = {each['website']: each for each in sitelist}.values()
siteJSON = {"urls": result}
with open("../data/output/fetch_emails.json", 'w') as fh:
    json.dump(siteJSON, fh)





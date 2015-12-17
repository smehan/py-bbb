"""
This class will take an existing list of sites encoded as a json object.
It will fetch those sites and find any emails on the target page or either
[about, contact] page and search those for email as well. It remembers what it's seen
from the source page to the target page to prevent tight loops. It returns the results
in a single json array.
"""
import urllib2
import httplib
import re
import json
import errno
import glob


def extract_array(data):
    for k,v in data.iteritems():  # TODO should only grab v. will break on multi k,v
        return(v)

def write_results(data):
    path = '../data/output/results_r3.json'
    try:
        with open(path, 'w') as json_file:
            r = json.dump(data, json_file)
    except IOError as exc:
        if exc.errno != errno.EISDIR:
            raise


def get_bbb_json():
    path = '../data/output/results-2.json'
    files = glob.glob(path)
    for name in files:
        try:
            with open(name) as json_file:
                bbbJSON = json.load(json_file)
                # bbbList = extract_array(bbbJSON)
        except IOError as exc:
            if exc.errno != errno.EISDIR:
                raise  # Propagate other kinds of IOError.
    return(bbbJSON)

def get_targets():
    path = '../data/output/fetch_emails-2.json'
    files = glob.glob(path)
    targetList = []
    for name in files:
        try:
            with open(name) as json_file:
                targetJSON = json.load(json_file)
                targetList = extract_array(targetJSON)
        except IOError as exc:
            if exc.errno != errno.EISDIR:
                raise  # Propagate other kinds of IOError.
    return(targetList)


def get_page(url):
    try:
        response = urllib2.urlopen(url)
        page = response.read()
    except urllib2.HTTPError, e:
        page = None
        # print e.fp.read()
        # print("Fail for %s:" % url)
    except urllib2.URLError, e:
        page = None
        # print e.reason
        # print("Fail for %s:" % url)
    except httplib.BadStatusLine, e:
        page = None
        # print e.line
        # print("Fail for %s:" % url)
    return(page)


def find_sub_page_links(page):
    result = []
    p = re.compile(r'<a href="(http(s)?:\/\/[\w\/_\.]+)">[\w\s]*about[\w\s]*<\/a>', flags=re.IGNORECASE).search(page)
    if (p is None):
        p = []
    if (p):
        result.append(p.group(1))
    p = re.compile(r'<a href="(http(s)?:\/\/[\w\/_\.]+)">[\w\s]*contact[\w\s]*<\/a>', flags=re.IGNORECASE).search(page)
    if (p is None):
        p = []
    if (p):
        result.append(p.group(1))
    return(result)


def find_email(page, email, memory=None):
    result = re.compile(r'[\w\.]+@[\w]+\.[\w]+').findall(page)
    if (len(result) != 0):
        return(result)
    if (memory):
        return(result)
    sub_targets = find_sub_page_links(page)
    if (len(sub_targets) != 0):
        memory = sub_targets[0]
        sub_result = []
        for s in sub_targets:
            sub_page = get_page(s)
            if (sub_page):
                sub_result = find_email(sub_page, email, memory)
        if (len(sub_result)!=0):
            return(sub_result)
    if (len(result)==0):
        result = 'NULL'
    return(result)


def process_targets(targets):
    """
    :param targets: JSON type array with form [{'website':'http://my.com','email':'me@com'},...]
    :return: JSON type array [{'website':'http://my.com','email':'me@com','host_email':'better@com'},...]
    iterates through all targets to fetch t's page, find email in company page.
    Makes email list unique and all lowercase. Rolls up results in a similar
    JSON type array but with extra element of new email, possibly different to BBB email coming in.
    """
    result_entries = []
    for t in targets:
        page = get_page(t['website'])
        if (t['email']):
            bbb_email = t['email']
        else:
            bbb_email = None
        if (page):
            email = find_email(page, bbb_email)
        if (isinstance(email, list)):
            email = [e.lower() for e in email]
            email = list(set(email))
        entry = {'website': t['website'], 'email': bbb_email, 'host_email': email}
        print(entry)
        result_entries.append(entry)
    return(result_entries)


def munge_results(emails, bbb_data):
    result = []
    # result = [e.update(i) for e in bbb_data if e.has_key('website') for i in emails if e['website'] == i['website']]
    # print(result)
    for e in bbb_data:
        if (e.has_key('website')):
            for i in emails:
                if (e['website'] == i['website']):
                    e.update(i)
                    result.append(e)
                    break
        else:
            result.append(e)
    return(result)

def summarize_run(data):
    totals = {'records': 0, 'bbb': 0, 'host':0}
    for e in data:
        totals['records'] += 1
        if (e.has_key('email') and e['email'] != 'NULL'):
            totals['bbb'] += 1
        if (e.has_key('host_email') and e['host_email'] != 'NULL'):
            totals['host'] += 1
    print("\n\n\n %d records with %d BBB emails and %d host emails found" % (totals['records'], totals['bbb'], totals['host']))
    print("\n Efficiencies: %f BBB | %f host | %f None" % ((float(totals['bbb'])/float(totals['records'])), (float(totals['host'])/float(totals['records'])), (float(totals['records'] - totals['bbb'] - totals['host'])/float(totals['records']))))


def main():
    targets = get_targets()
    new_emails = process_targets(targets)
    big_json = get_bbb_json()
    new_array = munge_results(new_emails, big_json)
    write_results(new_array)
    summarize_run(new_array)

    #process_targets([{'website': 'http://www.petersonmoving.com', 'email': 'NULL'}])
    print("\n\n\n\n************************************\n\n\njob is finished")

if __name__ == '__main__':
    main()

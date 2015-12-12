import urllib2
import httplib
import re
import json
import errno
import glob


def extract_array(data):
    for k,v in data.iteritems():  # TODO should only grab v. will break on multi k,v
        return(v)


def get_targets():
    path = '../data/output/fetch_emails.json'
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
    for t in targets:
        page = get_page(t['website'])
        if (t['email']):
            bbb_email = t['email']
        else:
            bbb_email = None
        if (page):
            email = find_email(page, bbb_email)
        if (isinstance(email, list)):
            email = list(set(email))
        entry = {'website': t['website'], 'email': bbb_email, 'host_email': email}
        print(entry)


def main():
    targets = get_targets()
    process_targets(targets)
    #process_targets([{'website': 'http://www.petersonmoving.com', 'email': 'NULL'}])
    print("\n\n\n\n************************************\n\n\njob is finished")

if __name__ == '__main__':
    main()

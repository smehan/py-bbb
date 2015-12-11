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
    resultlist = []
    resultJSON = {}
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


def find_email(page, email):
    result = re.compile(r'[\w\.]+@[\w\.]+').findall(page)
    sub_targets = re.compile(r'<a href="([\w\.]+)">[\w\s]+about[\w\s]+</a>', flags=re.IGNORECASE).findall(page)
    print(sub_targets)

def process_targets(targets):
    for t in targets:
        print(t['website'])
        page = get_page(t['website'])
        if (t['email']):
            email = t['email']
        else:
            email = None
        if (page is not None):
            email = find_email(page, email)




def main():
    targets = get_targets()
    process_targets(targets)

if __name__ == '__main__':
    main()

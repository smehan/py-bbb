"""
This class takes the results in from csv and transforms it into a more dense dataset by merging duplicate
entities with different elements / characteristics.

output is another CSV.
"""
import csv
import sys
import re



def getDict(row):
    out_row = {}
    out_row['website'] = row[0]
    out_row['city'] = row[1]
    out_row['name'] = row[2]
    out_row['zip'] = row[3]
    out_row['started'] = row[4]
    out_row['accredited'] = row[5]
    out_row['bbb_url'] = row[6]
    out_row['phone'] = row[7]
    out_row['state'] = row[8]
    out_row['contact'] = row[9]
    out_row['contact_b'] = row[10]
    out_row['bbb_opened'] = row[11]
    out_row['email'] = row[12]
    out_row['alternates'] = row[13]
    out_row['rating'] = row[14]
    out_row['external_email'] = row[15]
    out_row['external_email_b'] = row[16]
    out_row['manager'] = row[17]
    out_row['type'] = row[18]
    out_row['category'] = row[19]
    out_row['external_email_c'] = row[20]
    out_row['fb'] = row[21]
    out_row['address'] = row[40]
    return(out_row)


def compareRows(last, next):
    if (last['website'] == next['website'] and last['city'] == next['city']):
        return True
    else:
        return False


def correctBBB(a,b):
    if (re.match(r'http://www.bbb.org', a)):
        return(a)
    else:
        return(b)


def correctEmail(a,b):
    if (re.match(r'\w+@', a)):
        return(a)
    else:
        return(b)


def correctName(a,b):
    if (re.match(r'http', a)):
        return(b)
    else:
        return(a)


def correctNumIs(a,b):
    if re.search(r'number', a):
        a = ''
    elif (re.search(r'number', b)):
        b = ''
    if a == '' and b != '':
        out = b
    else:
        out = a
    return out


def mergeRows(last, next):
    out = last
    for k in last.keys():
        if next[k] == '':
            continue
        if last[k] == '':
            out[k] = next[k]
        if last[k] != next[k]:
            if k == 'bbb_url':
                out[k] = correctBBB(last[k], next[k])
            if k == 'email':
                if last[k] == 'NULL' and last['external_email'] != '':
                    last[k] = last['external_email']
                out[k] = correctEmail(last[k], next[k])
            if k == 'external_email':
                if last[k] == 'NULL' and last['external_email'] != '':
                    last[k] = last['external_email']
                out[k] = correctEmail(last[k], next[k])
            if k == 'external_email_b':
                if last[k] == 'NULL' and last['external_email_b'] != '':
                    last[k] = last['external_email_b']
                out[k] = correctEmail(last[k], next[k])
            if k == 'name':
                out[k] = correctName(last[k], next[k])
            if k == 'type':
                out[k] = correctNumIs(last[k], next[k])
            if k == 'category':
                out[k] = correctNumIs(last[k], next[k])
            #print(k,out[k],last[k],next[k])
    return(out)

def initHeader(myDict):
    with open('../data/output/result-bbb-movers-20160104.csv', 'w') as output:
        row_writer = csv.writer(output)
        row_writer.writerow(myDict.keys())


def writeRecord(myDict):
    with open('../data/output/result-bbb-movers-20160104.csv', 'a') as output:
        row_writer = csv.writer(output)
        row_writer.writerow(myDict.values())


def countEmails(record, count):
    if (record['email'] != 'NULL'):
        count += 1
    elif (record['external_email'] != ''):
        count += 1
    elif (record['external_email_b'] != ''):
        count += 1
    return(count)


def main():
    with open('../data/input/result-bbb-movers-20151214.csv', 'rU') as input:
        rows_in = csv.reader(input)
        header = rows_in.next()
        initial = True
        row_count = 0
        no_www = 0
        email_count = 0
        initHeader(getDict(header))
        for row in rows_in:
            if (initial):
                last_record = getDict(row)
                initial = False
                continue
            if (last_record and last_record['website']):
                next_record = getDict(row)
                if (compareRows(last_record, next_record)):
                    last_record = mergeRows(last_record, next_record)
                else:
                    email_count = countEmails(last_record, email_count)
                    last_record = next_record
                    writeRecord(last_record)
            elif (last_record and last_record['website'] == ''):
                no_www += 1
                next_record = getDict(row)
                email_count = countEmails(last_record, email_count)
                print(last_record['email'], last_record['external_email'], last_record['external_email_b'])
                writeRecord(last_record)
                last_record = next_record
            row_count += 1
        print("%d rows processed, %d have no websites, %d have emails" % (row_count, no_www, email_count))


if __name__ == '__main__':
    main()
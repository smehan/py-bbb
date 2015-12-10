import json
import re
import os
import sys
import glob
import errno


FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)

# TODO probably remove
class ConcatJSONDecoder(json.JSONDecoder):
    def decode(self, s, _w=WHITESPACE.match):
        s_len = len(s)

        objs = []
        end = 0
        while end != s_len:
            obj, end = self.raw_decode(s, idx=_w(s, end).end())
            end = _w(s, end).end()
            objs.append(obj)
        return objs # #


path = '../data/input/*.json'
files = glob.glob(path)
for name in files:
    try:
        with open(name) as json_file:
            print(json_file)
            #print((json_file.read()))
            json_data = json.load(json_file)
            print(json_data)
    except IOError as exc:
        if exc.errno != errno.EISDIR:
            raise # Propagate other kinds of IOError.






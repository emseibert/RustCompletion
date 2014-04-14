# Extends Sublime Text autocompletion to find matches in all open
# files. By default, Sublime only considers words from the current file.

import sublime_plugin
import sublime
import re
import time
import os, sys
import subprocess

class AllAutocomplete(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):

        line = [view.substr(sublime.Region(view.line(l).a, l)) for l in locations]
        commandsOnLine = line[0].split(' ')
        lineToCall = commandsOnLine[len(commandsOnLine) - 1]
        matches = callRacer(lineToCall)
        return matches

def callRacer(s):
    #os.environ['RUST_SRC_PATH'] = "/Users/emilyseibert/rust/src"
    os.environ['RUST_SRC_PATH'] = '/home/student/rust/src'
    #cmd = "/Users/emilyseibert/racer/bin/racer complete " + s
    cmd = 'cd /home/student/CS4414FinalProject/racer/bin/; ./racer complete ' + s
    (stdout, stderr) = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    results = []
    limit = 0
    for line in stdout.splitlines():
        if limit > 5:
            break
        elif line != b'':
            splitLine = str(line).split(',')
            matched = splitLine[len(splitLine) - 1]
            #print(str(matched))
            matched = str(parseLine(str(matched)))
            t =  (matched, matched)
            
            results.append(t)
            limit += 1

    return results

def parseLine(line):
    splitLine = line.split(' ')
    result = line
    #print(splitLine)
    #print(splitLine[0]=='pub')
    if (splitLine[0]=='pub' and splitLine[1]=='struct'):
        result = splitLine[2].split('<')[0]
    return result

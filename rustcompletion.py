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
        print("line")
        print(line)
        commandsOnLine = line[0].split(' ')
        print("commandsOnLine")
        print(commandsOnLine)
        isCrate = ""

        if (commandsOnLine[0] == "extern"):
            lineToCall = "";
            for s in commandsOnLine:
                lineToCall += s + " "
                isCrate = lineToCall
            if len(commandsOnLine) > 2:
                print("call this with crates:")
                print (callRacerCrates(commandsOnLine[len(commandsOnLine) - 1]))

                
        else:
            lineToCall = commandsOnLine[len(commandsOnLine) - 1]

        print("lineToCall")
        print(lineToCall)
        matches = callRacer(lineToCall)
        return matches

def callRacerCrates(s):
    os.environ['RUST_SRC_PATH'] = "/Users/emilyseibert/rust/src"
    cmd = "cd /Users/emilyseibert/Library/'Application Support'/'Sublime Text 3'/Packages/CS4414FinalProject/racer/bin/; ./racer crate-sort " + s
    (stdout, stderr) = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    results = stdout
    return results


def callRacer(s):
    os.environ['RUST_SRC_PATH'] = "/Users/emilyseibert/rust/src"
    #os.environ['RUST_SRC_PATH'] = '/home/student/rust/src'
    cmd = "cd /Users/emilyseibert/Library/'Application Support'/'Sublime Text 3'/Packages/CS4414FinalProject/racer/bin/; ./racer complete " + s
    #cmd = 'cd /home/student/CS4414FinalProject/racer/bin/; ./racer complete ' + s
    #cmd = 'cd "/home/student/.config/sublime-text-3/Packages/Complete/racer/bin/"; ./racer complete ' + s
    (stdout, stderr) = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    results = []
    #print(stdout)
    limit = 0
    for line in stdout.splitlines():
        if limit > 5:
            break
        elif line != b'':
            line = line.decode(encoding='UTF-8').strip()
            test = line
            if test[:6] == '#[path':
                continue
            matched = parseLine(line)
            t =  (matched, matched)
            
            results.append(t)
            limit += 1

    print(results)
    return results

def parseLine(line):
    splitLine = line.split(' ')
    result = line
    print(splitLine)
    if (splitLine[0]=='#[cfg(not(test))]'):
        splitLine.pop(0)
    if (splitLine[0]=='pub'): 
        if (splitLine[1]=='struct'):
            result = splitLine[2].split('<')[0]
        elif (splitLine[1]=='mod'):
            result = splitLine[2].split(';')[0]
        elif (splitLine[1]=='fn'):
            result = splitLine[2].split('<')[0]
        elif (splitLine[1]=='trait'):
            result = splitLine[2].split('<')[0]
    if (splitLine[0].strip()=="fn"):
            result = splitLine[1].split('(')[0].strip()
    if (splitLine[1].strip()=="fn"):
            result = splitLine[2].split('(')[0].strip()
    return result

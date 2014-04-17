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
        line_1 = line[0]
        print("len")
        print(str(len(line_1)))
        if len(line_1)>2:
            #Parse line to get all prior use's (let x = aa::bb::cc -> aa::bb)
            res = kfels_parse(prefix, line)
            regions = view.find_all(r'use (.*?)::%s'%res,)
        
            if len(regions) is not 0:
                #print("region: " + view.substr(regions[0]))
                line_1 = view.substr(regions[0]) + '::' + prefix

        commandsOnLine = line_1.split(' ')
        print("commandsOnLine")
        print(commandsOnLine)
        isCrate = ""
        matches = []

        if (commandsOnLine[0] == "extern"):
            lineToCall = "";
            for s in commandsOnLine:
                lineToCall += s + " "
                isCrate = lineToCall
            if len(commandsOnLine) > 2:
                matches = callRacerCrates(commandsOnLine[len(commandsOnLine) - 1])

                
        else:
            lineToCall = commandsOnLine[len(commandsOnLine) - 1]
            matches = callRacer(lineToCall)

        print("lineToCall")
        print(lineToCall)
        
        return matches

def callRacerCrates(s):
    #os.environ['RUST_SRC_PATH'] = "/Users/emilyseibert/rust/src"
    os.environ['RUST_SRC_PATH'] = '/home/student/rust/src'
    #os.environ['RUST_SRC_PATH'] = '/home/student/.config/sublime-text-3/Packages/CS4414FinalProject/rust/src'

    results = []
    for dirs in os.listdir(os.environ['RUST_SRC_PATH']):
        if dirs.find("lib" + s, 0) > -1:
            r = (dirs.split('lib')[1] + ";", dirs.split('lib')[1] + ";")
            results.append(r)

    return (results)


def kfels_parse(prefix,line):
    new_prefix = ''
    reg2 = re.match(r'.*?([a-zA-Z\d::]+)::%s'%prefix, line[0])
    if reg2 is not None:
        pre_pref = reg2.groups(1)
        if pre_pref is not []:
            new_prefix = pre_pref[0]
    return new_prefix

def callRacer(s):
    #os.environ['RUST_SRC_PATH'] = "/Users/emilyseibert/rust/src"
    os.environ['RUST_SRC_PATH'] = '/home/student/rust/src'
    #cmd = "cd /Users/emilyseibert/Library/'Application Support'/'Sublime Text 3'/Packages/CS4414FinalProject/racer/bin/; ./racer complete " + s
    #os.environ['RUST_SRC_PATH'] = '/home/student/.config/sublime-text-3/Packages/CS4414FinalProject/rust/src'
    #cmd = "/Users/emilyseibert/racer/bin/racer complete " + s
    #cmd = 'cd /home/student/.config/sublime-text-3/Packages/CS4414FinalProject/racer/bin/; ./racer complete ' + s
    cmd = 'cd /home/student/CS4414FinalProject/racer/bin/; ./racer complete ' + s
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
            result = splitLine[2].split('<')[0] + ";"
        elif (splitLine[1]=='mod'):
            result = splitLine[2].split(';')[0] + ";"
        elif (splitLine[1]=='fn'):
            result = splitLine[2].split('<')[0] + ";"
        elif (splitLine[1]=='trait'):
            result = splitLine[2].split('<')[0] + ";"
        elif (splitLine[1]=='enum'):
            result = splitLine[2].split('<')[0] + ";"
    if (splitLine[0].strip()=="fn"):
            result = splitLine[1].split('(')[0].strip() + "()"
    if (splitLine[1].strip()=="fn"):
            result = splitLine[2].split('(')[0].strip() + "()"
    return result 

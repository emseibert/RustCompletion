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
        line_1 = line[0]
        if prefix == 'use' and len(line_1)<3:
            return [('use','use')]
        if len(line_1)>2:
            #Parse line to get all prior use's (let x = aa::bb::cc -> aa::bb)
            res = kfels_parse(prefix, line)
            if res is not '':
                regions = view.find_all(r'use (.*?)::%s'%res,)
            
                if len(regions) is not 0:
                    #print("region: " + view.substr(regions[0]))
                    line_1 = view.substr(regions[0]) + '::' + prefix
                    
            

        commandsOnLine = line_1.split(' ')
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
        #print("lineToCall")
        #print(lineToCall)
        matches_no_dup = without_duplicates(matches)
        return matches_no_dup

def callRacerCrates(s):
    RUST_SRC = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rust_src'))
    results = []
    for dirs in os.listdir(RUST_SRC):
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
    rust_src = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rust_src'))
    #rust_src = "/Users/emilyseibert/rust/src"
    cmd_loc = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'racer/bin'))

    cmd = 'cd "' + cmd_loc + '"; ./racer complete "' + rust_src + '" '+ s
    print(cmd)
    (stdout, stderr) = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    results = []
    limit = 0
    for line in stdout.splitlines():
        if limit > 5:
            break
        elif line != b'':
            line = line.decode(encoding='UTF-8').strip()
            test = line
            if test[:6] == '#[path':
                continue

            #remove commented code and test functions from results
            if test.startswith('//') or test.startswith('test!('): #remove commented code and test functions
                #print(test + " is a comment")
                continue
            #print("before: " + line)
            matched_reg = re.match(r'(?:pub)*(?:\s)*(?:fn|mod|struct)\s*(.*)(?:{|;)', line)
            matched = parseLine(line)
            matched_full = matched
            if matched_reg is not None:
                #print("match_reg")
                matched_full = matched_reg.groups(1)[0]
                #print(matched_full)
            #else:
                #print("NONE")
            #print("after: " + matched)
            t =  (matched_full, matched)
            
            results.append(t)
            limit += 1

   # print(results)
    return results

def parseLine(line):
    #print (line)
    splitLine = line.split(' ')
    result = line
   # print(splitLine)
    if (splitLine[0]=='#[cfg(not(test))]'):
        splitLine.pop(0)
    if (splitLine[0]=='pub'): 
        if (splitLine[1]=='struct'):
            result = splitLine[2].split('<')[0] + ";"
        elif (splitLine[1]=='mod'):
            result = splitLine[2].split(';')[0] + ";"
        elif (splitLine[1]=='fn'):
            result = splitLine[2].split('<')[0] + "()"
        elif (splitLine[1]=='trait'):
            result = splitLine[2].split('<')[0] + ";"
        elif (splitLine[1]=='enum'):
            result = splitLine[2].split('<')[0] + ";"
        elif (splitLine[1].strip()=='unsafe'):
            if (splitLine[2].strip()=='fn'):
                if splitLine[3].strip().find('<') > -1:
                    result = splitLine[3].strip().split('<')[0] + "()"
                else:
                    result = splitLine[3].split('(')[0].strip() + "()"
    if (splitLine[0].strip()=="fn"):
            if splitLine[1].strip().find('<') > -1:
                result = splitLine[1].strip().split('<')[0] + "()"
            else:
                result = splitLine[1].split('(')[0].strip() + "()"
    if (splitLine[1].strip()=="fn"):
            if splitLine[2].find('<') > -1:
                result = splitLine[2].strip().split('<')[0] + "()"
            else:
                result = splitLine[2].split('(')[0].strip() + "()"
    return result 

# keeps first instance of every word and retains the original order
def without_duplicates(words):
    result = []
    for w in words:
        if w not in result:
            result.append(w)
    return result

# keeps first instance of every word and retains the original order
def without_duplicates(words):
    result = []
    for w in words:
        if w not in result:
            result.append(w)
    return result

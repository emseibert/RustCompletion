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
        #only proceed if currently writing in Rust
        if self.is_enabled():
            functionCompletions = []
            matches = []

            line = [view.substr(sublime.Region(view.line(l).a, l)) for l in locations]
            line_1 = line[0]

            #if the prefix is &, then the get the lifetimes currently in the line
            if prefix == "":
                return get_all_lifetimes(line_1)

            #gets the word completions from Sublime
            view_words = view.extract_completions(prefix, locations[0])
            
            #gets region coordinates for all functions in text file
            function_regions = view.find_by_selector('meta.function')
            
            
            list_of_fn_names = []        
            #iterates over each function region and parses for function that have same prefix
            for region in function_regions:
                line2 = view.line(region)
                strLine = view.substr(line2)
                list_of_fn_names.append(getFnNames(strLine))
                functionCompletions += functionParse(prefix, strLine)

            view_words = without_fn_dups(view_words, list_of_fn_names)

            formatWords = []
            for w in view_words:
                t = (str(w), str(w))
                formatWords.append(t)

            matches += formatWords

            #disallows autocompletion when prefix is libc since this was extremely time consuming
            if prefix == "libc":
                return[('','')]
            
            if prefix == 'use' and len(line_1)<3:
                return [('use','use')]
            if len(line_1)>2:
                #Parse line to get all prior use's (let x = aa::bb::cc -> aa::bb)
                res = kfels_parse(prefix, line)
                
                if res is not '':
                    regions = view.find_all(r'use (.*?)::%s'%res,)
                
                    if len(regions) is not 0:
                        line_1 = view.substr(regions[0]) + '::' + prefix
                        

            commandsOnLine = line_1.split(' ')
            isCrate = ""

            if (commandsOnLine[0] == "extern"):
                lineToCall = "";
                for s in commandsOnLine:
                    lineToCall += s + " "
                    isCrate = lineToCall
                if len(commandsOnLine) > 2:
                    matches += callRacerCrates(commandsOnLine[len(commandsOnLine) - 1])         
            else:
                lineToCall = commandsOnLine[len(commandsOnLine) - 1]
                matches += callRacer(lineToCall)
            
            matches_no_dup = functionCompletions + without_duplicates(matches)

            return matches_no_dup

    def on_modified(self, view):
        #only proceed if currently writing in Rust
        if self.is_enabled():
            for region in view.sel():  
                # Only interested in empty regions, otherwise they may span multiple  
                # lines, which doesn't make sense for this command.  
                if region.empty():   
                    # Expand the region to the full line it resides on, excluding the newline  
                    line = view.line(region)
                    lineContents = view.substr(line)

                    #parses the line and removes double single quotes if they follow "<" or "&" or "< ?,"
                    if "fn" in lineContents:
                        if "&''" in lineContents:
                            reg_m = re.match(r'(?P<begin>.*)&''',lineContents)
                            if reg_m is not None:
                                begin = reg_m.group('begin')
                                pos = view.sel()[0].begin()
                                #replace '' with '
                                view.run_command("view_replace", { "begin" : view.sel()[0].begin()+1, "end": view.sel()[0].end(), "name": " " });
                        
                        if "<''" in lineContents:
                            reg_m = re.match(r'(?P<begin>.*)<''',lineContents)
                            if reg_m is not None:
                                begin = reg_m.group('begin')
                                pos = view.sel()[0].begin()
                                #replace '' with '
                                view.run_command("view_replace", { "begin" : view.sel()[0].begin()+1, "end": view.sel()[0].end(), "name": " " });
                        elif "<'" in lineContents:
                            reg_m = re.match(r"(?P<begin>.*fn.*<'[a_zA_Z](,[\s]*'[\s]*(\w))*),[\s]*''", lineContents)
                            if reg_m is not None:
                                begin = reg_m.group('begin')
                                pos = view.sel()[0].begin()
                                #replace '' with '
                                view.run_command("view_replace", { "begin" : view.sel()[0].begin()+1, "end": view.sel()[0].end(), "name": " " });
                                 
    #Returns true if the syntax of the active view is set to Rust, 
    def is_enabled(self):
        if str(sublime.active_window().active_view().settings().get('syntax')) == 'Packages/Rust/Rust.tmLanguage':
            return True
        else:
            return False

def without_fn_dups(sublimeList, fnList):
    matches = []

    for s in sublimeList:
        if s not in fnList:
            matches.append(s)


    return matches

def getFnNames(strLine):
    removeFn = strLine.split('fn ')[1]
    getName = removeFn.split('(')[0]
    return getName

def callRacerCrates(s):
    RUST_SRC = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rust_src'))
    results = []
    for dirs in os.listdir(RUST_SRC):
        if dirs.find("lib" + s, 0) > -1:
            r = (dirs.split('lib')[1] + ";", dirs.split('lib')[1] + ";")
            results.append(r)

    return (results)

def functionParse(prefix, line):
    matches = []
    fn = line.split("fn ")[1]
    if fn[0] == prefix:
        fn_name = line.split('(')[0]
        r = (str(fn.split(')')[0]) + ")", formatFn(fn))
        matches.append(r)

    return matches

def formatFn(function):
    paramVars = []
    name = function.split('(')[0]
    paramOutput = name+ "("
    paramString = function.split('(')[1].split(')')[0]
    indexOfColon = find(paramString, ':')
    count = 0
    
    for i in indexOfColon:
        
        if count == (len(indexOfColon)-1):
            paramOutput += "${" + str(count+1) + ":" + getParam(i, paramString) + "})"
        else:
            paramOutput = paramOutput + "${" + str(count+1) + ":" + getParam(i, paramString)+ "}" + ", "
        
        count+=1
    return paramOutput

def getParam(index, string):
    param = ""

    while (string[index] == ' ' or string[index] == ':'):
        index -= 1

    while (string[index] != ' ' and string[index] != ',' and index >= 0):
        param = string[index] + param
        index -= 1

    return param

def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

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
    cmd_loc = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'racer/bin'))

    cmd = 'cd "' + cmd_loc + '"; ./racer complete "' + rust_src + '" '+ s

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
            if test.startswith('//') or test.startswith('test!(') or test.startswith('iotest!'): 
                continue

            matched_reg = re.match(r'(?:pub)*(?:\s)*(?:fn|mod|struct)\s*(.*)(?:{|;)', line)
            matched = parseLine(line)
            matched_full = matched

            if matched_reg is not None:
                matched_full = matched_reg.groups(1)[0]
                
            t =  (matched_full, matched)
            
            results.append(t)
            limit += 1
    
    
    return results

def parseLine(line):
    
    splitLine = line.split(' ')
    result = line

    if (splitLine[0]=='#[cfg(not(test))]'):
        splitLine.pop(0)

    if (splitLine[0]=='pub'): 
        if (splitLine[1]=='struct'):
            result = splitLine[2].split('<')[0]

        elif (splitLine[1]=='mod'):
            result = splitLine[2].split(';')[0]

        elif (splitLine[1]=='fn'):
            result = splitLine[2].split('<')[0] + "()"

        elif (splitLine[1]=='trait'):
            result = splitLine[2].split('<')[0]

        elif (splitLine[1]=='enum'):
            result = splitLine[2].split('<')[0]

        elif (splitLine[1].strip()=='unsafe'):
            if (splitLine[2].strip()=='fn'):
                result = parse_rust_func(line)

    if (splitLine[0].strip()=="fn"):
            result = parse_rust_func(line)

    if (splitLine[1].strip()=="fn"):
            result = parse_rust_func(line)

    return result 

def parse_rust_func(line):
    result = line
    reg = re.match(r'(?:pub)*(?:\s)*(?:unsafe)*(?:\s)*(?:fn)\s*(?P<func>\b(?:\w)*\b(?:<(?:.*)>)*)(?:\((?P<args>[^)]*)\))(?:.*)(?:{)*(?:;)*', line)
    
    if reg is not None:
        func = reg.group('func') + "("
        result = func
        func_list = func.split('<')

        if len(func_list) >1:
            result = func_list[0] + "("

        args = reg.group('args')
        args_list = args.split(',')
        if len(args_list) >=1:
            result += '${1:'+(args_list[0].split(':')[0])+'}'
            args_list.pop(0)

        if len(args_list) >= 1:
            i = 2
            for x in args_list:
                result += ', ${'+str(i)+':' + x.split(':')[0] + '}'
                i += 1
        result += ')'

    return result

# keeps first instance of every word and retains the original order
def without_duplicates(words):
    result = []
    for w in words:
        if w not in result:
            result.append(w)
    return result

#gets all the lifetime variables in lines
def get_all_lifetimes(line):
    result = []
    line_2 = line.split('<')
    if len(line_2)>1:
        line_3 = line_2[1].split('>')
        line_4 = line_3[0].split(',')
        for x in line_4:
            result.append((x.strip(),x.strip()))
    return result
    
class ViewReplaceCommand(sublime_plugin.TextCommand):
  def run(self, edit, begin, end, name):
    self.view.replace(edit, sublime.Region(begin, end), name)

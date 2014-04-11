# Extends Sublime Text autocompletion to find matches in all open
# files. By default, Sublime only considers words from the current file.

import sublime_plugin
import sublime
import re
import time
import os, sys
import subprocess

# limits to prevent bogging down the system
MIN_WORD_SIZE = 3
MAX_WORD_SIZE = 50

MAX_VIEWS = 20
MAX_WORDS_PER_VIEW = 100
MAX_FIX_TIME_SECS_PER_VIEW = 0.01
string = ""


def print_to_console(word):
        f = open('out.txt', 'w')
        string = '\n'.join(str(word))
        f.write(str(word))
        f.close()


class AllAutocomplete(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):
        print("prefix: " + prefix)
       # print_to_console("fuck you")
        #print_to_console("prefix: " + prefix)
        #print_to_console(locations)
        # global string

        # if prefix != " ":
        #     string += prefix
        # else:
        #     string = ""

        # print string
        # words = []
        # # # Limit number of views but always include the active view. This
        # # # view goes first to prioritize matches close to cursor position.
        # other_views = [v for v in sublime.active_window().views() if v.id != view.id]
        # views = [view] + other_views
        # views = views[0:MAX_VIEWS]

        # for v in views:
        #     if len(locations) > 0 and v.id == view.id:
        #         view_words = v.extract_completions(prefix, locations[0])
        #     else:
        #         view_words = v.extract_completions(prefix)
        #     view_words = filter_words(view_words)
        #     view_words = fix_truncation(v, view_words)
        #     words += view_words

        # words = without_duplicates(words)
        # matches =  [(w, w.replace('$', '\\$')) for w in words]
        # print(matches)
        matches = callRacer(prefix)
        print (matches)
        return matches


def filter_words(words):
    words = words[0:MAX_WORDS_PER_VIEW]
    return [w for w in words if MIN_WORD_SIZE <= len(w) <= MAX_WORD_SIZE]

# keeps first instance of every word and retains the original order
# (n^2 but should not be a problem as len(words) <= MAX_VIEWS*MAX_WORDS_PER_VIEW)
def without_duplicates(words):
    result = []
    for w in words:
        if w not in result:
            result.append(w)
    return result


# Ugly workaround for truncation bug in Sublime when using view.extract_completions()
# in some types of files.
def fix_truncation(view, words):
    fixed_words = []
    start_time = time.time()

    for i, w in enumerate(words):
        #The word is truncated if and only if it cannot be found with a word boundary before and after

        # this fails to match strings with trailing non-alpha chars, like
        # 'foo?' or 'bar!', which are common for instance in Ruby.
        match = view.find(r'\b' + re.escape(w) + r'\b', 0)
        truncated = is_empty_match(match)
        if truncated:
            #Truncation is always by a single character, so we extend the word by one word character before a word boundary
            extended_words = []
            view.find_all(r'\b' + re.escape(w) + r'\w\b', 0, "$0", extended_words)
            if len(extended_words) > 0:
                fixed_words += extended_words
            else:
                # to compensate for the missing match problem mentioned above, just
                # use the old word if we didn't find any extended matches
                fixed_words.append(w)
        else:
            #Pass through non-truncated words
            fixed_words.append(w)


        # if too much time is spent in here, bail out,
        # and don't bother fixing the remaining words
        if time.time() - start_time > MAX_FIX_TIME_SECS_PER_VIEW:
            return fixed_words + words[i+1:]

    return fixed_words

if sublime.version() >= '3000':
  def is_empty_match(match):
    return match.empty()
else:
  def is_empty_match(match):
    return match is None

def callRacer(s):
    global string
    os.environ['RUST_SRC_PATH'] = "/Users/emilyseibert/rust/src"
    if s != " ":
        string += s
    else:
        string = ""

    cmd = "/Users/emilyseibert/racer/bin/racer complete " + string
    print("cmd: " + cmd)

    (stdout, stderr) = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
    results = []
    limit = 0
    for line in stdout.splitlines():
        if limit > 5:
            break
        elif line != b'':

            print(line)
            t =  (str(line), str(line))
            results.append(t)
            limit += 1

    return results


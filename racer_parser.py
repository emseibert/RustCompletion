import subprocess

# note that racer doesn't work with these modifications to find std::io or std::io:: suggestions that aren't functions

def callRacer(string):
    cmd = "/Users/emilyseibert/racer/bin/racer complete " + string
    proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
    limit = 0
    words = []
    while (limit < 5):
       #the real code does filtering here
           line = proc.stdout.readline()
           line = proc.stdout.readline()
           print "hi: " + line

           if line != '':
               #print "line: " + line
               #ret = line.split(',')

               ##remove *some* commented out code from lib, doesn't work for lines in /* */
               #if ret[4].strip()[0] != '#':

                   #outputList = ret[len(ret)-1].split(' ')

                   #only suggest if it's a pub method
                   #if outputList[0] == "pub":
                       #words.append(outputList[2])
                words.append(line)
                limit += 1
                       #limit += 1
           else:
               print "break"
               break
    return words
    # cmd = "/Users/emilyseibert/racer/bin/racer complete " + string
    # proc = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE)
    # limit = 0
    # words = []
    # while (limit < 5):
    #    #the real code does filtering here
    #        line = proc.stdout.readline()
    #        line = proc.stdout.readline()
    #
    #        if line != '':
    #            #print "line: " + line
    #            ret = line.split(',')
    #
    #            #remove *some* commented out code from lib, doesn't work for lines in /* */
    #            if ret[4].strip()[0] != '#':
    #
    #                outputList = ret[len(ret)-1].split(' ')
    #
    #                #only suggest if it's a pub method
    #                if outputList[0] == "pub":
    #                    print outputList[2]
    #                    words.append(outputList[2])
    #                    limit += 1
    #        else:
    #            break
    #
    # return words

def main():
    string = raw_input("autocomplete: ")
    print callRacer(string)

if __name__ == "__main__":
    main()
#!/usr/bin/python
#
# ============================================================================
# FILE: python/stardict.py
# AUTHOR: Phong V. Cao <phongvcao@phongvcao.com>
# License: MIT license {{{
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# }}}
# ============================================================================


import sys
import os
import locale
import re
from subprocess import Popen, PIPE


def main():
    sys.stdout.write(getDefinition([sys.argv[1:]], caller="bash"))


def processArgsList(argsList):
    startArgPattern = "^(?:\\\"|\\').*"
    endArgPattern = ".*(?:\\\"|\\')$"
    finalArgsList = []
    i = 0

    while True:
        startArgIdx = i

        if (re.match(startArgPattern, argsList[i])):
            # If the current element matches the startArgPattern,
            # We keep incrementing i until being able to find
            # endArgPattern, or until i == len(argsList)
            while ((i < len(argsList)) and
                    not(re.match(endArgPattern, argsList[i]))):
                i += 1

            endArgIdx = i
            tempList = argsList[startArgIdx:endArgIdx + 1]

            if (re.match(endArgPattern, argsList[i])):
                finalArgsList.append(" ".join(tempList))
            else:
                finalArgsList += tempList

        else:
            finalArgsList.append(argsList[i])

        i += 1
        if (i >= len(argsList)):
            break

    return finalArgsList


def getDefinition(argsListList, caller="vim"):
    argsListList[0].insert(0, "-n")
    argsListList[0].insert(0, "sdcv")

    f = open("/tmp/vim-stardict-output.txt", "w")
    f.write(str(argsListList))
    f.close()

    definition = Popen(" ".join(argsListList[0]), shell=True, stdout=PIPE)\
            .stdout.read()
    encoding = locale.getdefaultlocale()[1]
    definition = formatStr(definition.decode(encoding))

    if (caller == "bash"):
        stardictResult = "[A-Z].*"
        stardictWord = "\\@.*"
        stardictWordType = "\\*.*"
        stardictWordMeaning = "[0-9].*"
        stardictWordExample = "(    \\-\\s.*\\:|\\!.*|    \\-\\s.*)"
        stardictDictName = "\\@[^/]*\\:[^/]*"
        # The color codes were generated by running the following commands
        # in bash:
        #
        # for (( i = 0; i < 17; ++i ));
        # do echo "$(tput setaf $i)This is ($i) $(tput sgr0)";
        # done
        #
        # http://stackoverflow.com/a/25692021
        #

        nc = "\033[0m"
        preProcSubStr = os.environ["STARDICT_WORD"] + "\\1" + nc
        specialSubStr = os.environ["STARDICT_RESULT"] + "\\1" + nc
        statementSubStr = os.environ["STARDICT_WORD_TYPE"] + "\\1" + nc
        identifierSubStr = os.environ["STARDICT_WORD_MEANING"] + "\\1" + nc
        typeSubStr = os.environ["STARDICT_WORD_EXAMPLE"] + "\\1" + nc
        underlinedSubStr = os.environ["STARDICT_DICT_NAME"] + "\\1" + nc

        finalStr = ""
        replacedStr = ""
        startLineCharIdx = -1

        while True:
            endLineCharIdx = definition.find('\n', startLineCharIdx + 1)

            if (endLineCharIdx < 0):
                break

            # Also include newline as part of the extracted string
            line = definition[startLineCharIdx + 1:endLineCharIdx + 1]

            if (re.match("^" + stardictResult, line)):
                # Re-format stardictResult
                replacedStr = re.sub("^(" + stardictResult + ")",
                        specialSubStr, line, flags=re.IGNORECASE)

            elif (re.match("^" + stardictDictName, line)):
                # Re-format stardictDictName
                replacedStr = re.sub("^(" + stardictDictName + ")",
                        underlinedSubStr, line, flags=re.IGNORECASE)

            elif (re.match("^" + stardictWord, line)):
                # Re-format stardictWord
                replacedStr = re.sub("^(" + stardictWord + ")", preProcSubStr,
                        line, flags=re.IGNORECASE)

            elif (re.match("^" + stardictWordType, line)):
                # Re-format stardictWordType
                replacedStr = re.sub("^(" + stardictWordType + ")",
                        statementSubStr, line, flags=re.IGNORECASE)

            elif (re.match("^" + stardictWordMeaning, line)):
                # Re-format stardictWordMeaning
                replacedStr = re.sub("^(" + stardictWordMeaning + ")",
                        identifierSubStr, line, flags=re.IGNORECASE)

            elif (re.match("^" + stardictWordExample, line)):
                # Re-format stardictWordExample
                replacedStr = re.sub("^(" + stardictWordExample + ")",
                        typeSubStr, line, flags=re.IGNORECASE)

            else:
                replacedStr = line

            finalStr += replacedStr
            startLineCharIdx = endLineCharIdx

        return finalStr

    return definition


def formatStr(outputStr):
    replacedBullet = 1
    wordMeaningPattern = "^\\-\\s+.*"
    wordExamplePattern = "^[=+].*"
    wordMultiExamplesPattern = "^\\!.*"
    wordPattern = "^\@.*"
    dictNamePattern = "^\\-\\-\\>.*"
    finalStr = ""

    startLineCharIdx = -1
    prevLineCharIdx = -1

    while True:
        endLineCharIdx = outputStr.find('\n', startLineCharIdx + 1)

        if (endLineCharIdx < 0):
            break

        # Also include newline as part of the extracted string
        line = outputStr[startLineCharIdx + 1:endLineCharIdx + 1]

        # The order of the if/elseif statements matter to the logic flow of
        # this function
        if (re.match(wordExamplePattern, line)):
            # Re-format WordExample
            replacedStr = re.sub("^[=+]\\s*", "    - ", line,
                    flags=re.IGNORECASE)
            replacedStr = re.sub("\\+\\s*", ": ", replacedStr,
                    flags=re.IGNORECASE)
            finalStr += replacedStr

        elif (re.match(wordMeaningPattern, line)):
            # Re-format WordMeaning
            if (prevLineCharIdx > -1):
                prevLine = outputStr[prevLineCharIdx + 1:startLineCharIdx + 1]

                if (re.match(wordMultiExamplesPattern, prevLine)):
                    replacedStr = re.sub("^\\-", "        -", line,
                            flags=re.IGNORECASE)
                else:
                    replacedStr = re.sub("^\\-\\s+", str(replacedBullet) +
                            ". ", line, flags=re.IGNORECASE)
                    replacedBullet += 1
            finalStr += replacedStr

        elif (re.match(wordPattern, line)):
            # Re-format Word
            # replacedStr = re.sub("^\\@([^/0-9]+)", "\\1:", line,
                    # flags=re.IGNORECASE)
            # finalStr += replacedStr
            finalStr += line
            replacedBullet = 1
        else:
            finalStr += line

        prevLineCharIdx = startLineCharIdx
        startLineCharIdx = endLineCharIdx

    finalStr2 = ""
    replacedBullet = 1
    startLineCharIdx = -1

    while True:
        endLineCharIdx = finalStr.find('\n', startLineCharIdx + 1)

        if (endLineCharIdx < 0):
            break

        # Also include newline as part of the extracted string
        line = finalStr[startLineCharIdx + 1:endLineCharIdx + 1]

        if (re.match(wordMultiExamplesPattern, line)):
            replacedStr = re.sub("^\\!(.*)", "    - \\1:", line,
                    flags=re.IGNORECASE)
            finalStr2 += replacedStr

        elif (re.match(dictNamePattern, line)):
            replacedStr = re.sub("^\\-\\-\\>", "@Dictionary: ", line,
                    re.IGNORECASE)
            finalStr2 += replacedStr

            startLineCharIdx = endLineCharIdx
            endLineCharIdx = finalStr.find('\n', startLineCharIdx + 1)
            line = finalStr[startLineCharIdx + 1:endLineCharIdx + 1]

            replacedStr = re.sub("^\\-\\-\\>", "@SearchedTerm: ", line,
                    re.IGNORECASE)
            finalStr2 += replacedStr
        else:
            finalStr2 += line

        startLineCharIdx = endLineCharIdx

    return finalStr2


if __name__ == "__main__":
    main()

import os
import fitz #PyMuPDF -- reads the text in a more useable format than PyPDF
import re
import json

def get_author(page, relatedString):
    title_page = page.get_text()
    title_list = title_page.splitlines()
    for m, s in enumerate(title_list):
        if relatedString in s:
            author = title_list[m+1]
    return author

def getWords_ySorted(p):
    # sort words by text_y coordinate
    WordTuples = p.get_textpage().extractWORDS()
    WordTuples.sort(key=lambda x: x[3])
    return WordTuples

def extractRemoveTitle(wordTups):
    q = 0
    title_string = []
    for item in wordTups:
        if item[5] == 0:
            title_string.append(item[4])
            q += 1
    title_string = " ".join(word for word in title_string)
    newTuples = wordTups[q:]
    return newTuples, title_string

def reblockAndSort(wordTups, removeHeader=True, removeFooter=True, anticipateTable=True):
    # group words by block num
    blocks = []
    subblock = []
    ia = 0
    tups = wordTups

    if removeHeader:
        noggin = wordTups[0][5]
        tups = [tup for tup in tups if tup[5] != noggin]

    if removeFooter:
        tootsies = wordTups[-1][5]
        tups = [tup for tup in tups if tup[5] != tootsies]
    
    if anticipateTable:
        Dropsies = []
        for ix, tup in enumerate(tups):
            if ix == 0:
                continue
            elif tup[5] in Dropsies:
                continue
            else:
                prevTup = tups[ix-1]
                if (tup[1] == prevTup[1]) and (abs(tup[2] - prevTup[2]) > 40) and (tup[5] != prevTup[5]):
                    Dropsies.append(tup[5])

    for ix, item in enumerate(tups):
        # Sorted by y_text coord.
        if ix == 0:
            subblock.append(item)

        elif item[5] == subblock[ia][5]:
            subblock.append(item)
            ia += 1                             # track subblock
        
        else:                                   # Append subgroups to page block
            blocks.append(subblock)
            ia = 0
            subblock = []
            subblock.append(item)
            
    blocks.append(subblock)

    flattenedBlocks = [item for items in blocks for item in items if item[5] not in Dropsies]
    return flattenedBlocks

def ProperSortString(smushedBlox, lineSpaceVal=5):
    final_sort = []
    subfinal_sort = []
    for ix, item in enumerate(smushedBlox):
        
        if ix == 0:
            subfinal_sort.append(item)

        elif item[3] == smushedBlox[ix-1][3]:
            subfinal_sort.append(item)
        
        elif abs(item[3] - smushedBlox[ix-1][3]) <= lineSpaceVal:
            subfinal_sort.append(item)

        else:
            subfinal_sort.sort(key = lambda x: x[0])
            final_sort.append(subfinal_sort)
            subfinal_sort = []
            subfinal_sort.append(item)
    
    subfinal_sort.sort(key= lambda x: x[0])
    final_sort.append(subfinal_sort)

    flattenFinalSort = [item[4] for items in final_sort for item in items]

    return flattenFinalSort

# returns dictionary with author, title, and full string.
# Headers and Footers are removed, while citations and bibliography are left in.
def pdfToDict(pdf, authorLocutor):
    Strings = []
    dict_ = {}
    with fitz.open(pdf) as file:
        for i, page in enumerate(file):
            if i == 0:
                dict_["author"] = get_author(page, authorLocutor)
            
            else:
                wordTuples = getWords_ySorted(page)
                if i == 1:
                    wordTuples, dict_["title"] = extractRemoveTitle(wordTuples)
                
                blockedAndSorted = reblockAndSort(wordTuples)
                sortedStringy = ProperSortString(blockedAndSorted)
                strCheese = ' '.join(item for item in sortedStringy)
                Strings.append(strCheese)

    dict_["content"] = ' '.join(item for item in Strings)
    return dict_

# Sure, there are plenty of libraries to help convert characters for tokens. But I wanted to do it.
# TODO: refactor to use a list of tuples, rather than two separate lists
def removeProblemChars(string, charsToDrop, charsToReplace):
    string_cleaning = string
    for ix, chars in enumerate(charsToDrop):
        string_cleaning = string_cleaning.replace(chars, charsToReplace[ix])
    return string_cleaning

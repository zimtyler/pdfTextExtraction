# import fitz
# jdict = page.get_textpage().extractRAWDICT()
# Func takes advantage of the .extractRAWDICT() textpage method in PyMuPDF

def getWordTuples(jdict):
    WortUpps = []                                           # Main list, going to flatten in next funk
    for block in jdict["blocks"]:                    
        for line in block["lines"]:
            for span in line["spans"]:
                spanWords = []                              # list holding wordTups
                charWord = ""                               # list holding individual wordTup info
                x0 = 0.0                                    # x0 of first char in word
                yOrigin = span["chars"][0]["origin"][1]     # y origin of all chars in line
                size = span["size"]                         # return font size 
                font = span["font"]                         # return font type (STIXGeneral-Regular generates new block)
                i_last = len(span["chars"]) - 1
                for i, char in enumerate(span["chars"]):
                    if x0 == 0.0:
                        x0 += char["bbox"][0]

                    if char["c"] != " ":
                        charWord += char["c"]
                    else:                                   # if pdf is improperly formatted: if i != 0
                        wordTup = (x0, span["chars"][i-1]["bbox"][2], yOrigin, charWord, size, font)
                        spanWords.append(wordTup)

                        spaceTup = (char["bbox"][0], char["bbox"][2], yOrigin, " ", size, font)
                        spanWords.append(spaceTup)

                        charWord = ""
                        x0 = 0.0

                    if i == i_last:
                        wordTup = (x0, char["bbox"][2], yOrigin, charWord, size, font)
                        spanWords.append(wordTup)
                WortUpps.append(spanWords)
              
    FlattyCakes = [item for items in WortUpps for item in items]
    return FlattyCakes

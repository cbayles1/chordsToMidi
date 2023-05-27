import re

def getChords(filepath):
    with open(filepath, 'rt', encoding="utf-8") as f:
        content = f.read()
        # Split the content
        data_list = re.split(r'\s+|\\n', content)
        # Remove any empty elements from the list
        data_list = list(filter(None, data_list))
        return data_list

def getRoot(chord):
    if len(chord) > 1 and (chord[1] == '#' or chord[1] == 'b'):
        return chord[0:2]
    return chord[0]

def parseChord(chord):
    root = getRoot(chord)
    print(root)
    
def parseAllChords(chords):
    for i in range(0, len(chords)):
        chord = chords[i]
        if chord[0] == '~':
            if i <= 0:
                raise Exception("You cannot start a progression with '~'!")
            else:
                chords[i] = chords[i-1]
                chord = chords[i-1]
        parseChord(chord)

#------------------------------------MAIN------------------------------------
chords = getChords('input.txt')
parseAllChords(chords)

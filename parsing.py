import re
from mingus.containers import Track
from mingus.containers import Bar
from mingus.containers import NoteContainer
from mingus.midi import midi_file_out

def getChords(filepath):
    with open(filepath, 'rt', encoding="utf-8") as f:
        content = f.read()
        data_list = re.split(r'\s+|\\n', content) #split on newlines and spaces
        data_list = list(filter(None, data_list))  # Remove any empty elements from the list
        return data_list

def getRoot(chord):
    if len(chord) > 1 and (chord[1] == '#' or chord[1] == 'b'):
        return chord[0:2]
    return chord[0]
     
def convertTildes(chords):
    for i in range(0, len(chords)):
        chord = chords[i]
        if chord[0] == '~':
            if i <= 0:
                raise Exception("You cannot start a progression with '~'!")
            else:
                chords[i] = chords[i-1]
                chord = chords[i-1]

def chordsToTrack(chords):
    t = Track()
    for chord in chords:
        nc = NoteContainer(chord)
        b = Bar()
        b.add_notes(chord)
        t.add_bar()
    return t

#------------------------------------MAIN------------------------------------
chords = getChords('input.txt')
convertTildes(chords)
track = chordsToTrack(chords)
midi_file_out.write_Track("test.mid", track)
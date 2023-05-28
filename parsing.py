import re
from mingus.containers import Track
from mingus.containers import Bar
from mingus.containers import NoteContainer
from mingus.midi import midi_file_out
import mingus.core.chords as mchords

def getHeader(filepath):
    with open(filepath, 'rt', encoding="utf-8") as f:
        header = f.readline().strip().split()
        header[1] = int(header[1]) #TEMPO
        header[2] = int(header[2]) #REPEAT
        return header

def getChords(filepath):
    with open(filepath, 'rt', encoding="utf-8") as f:
        f.readline() # skip header
        content = f.read()
        data_list = re.split(r'\s+|\\n', content) # split on newlines and spaces
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

def chordsToTrack(chords, addRoots=True):
    t = Track()
    for i in range(0, len(chords)):
        chord = chords[i]
        root = getRoot(chord)
        notes = mchords.from_shorthand(chord)
        
        nc = NoteContainer(notes)
        if addRoots: nc.add_note(root + "-2")
        
        b = Bar()
        b.place_notes(nc, 1) #2nd arg is note type, not length (whole, half, quarter...)
        t.add_bar(b)
    return t

#------------------------------------MAIN------------------------------------
infile = 'input.txt'
header = getHeader(infile)
chords = getChords(infile)
convertTildes(chords)
track = chordsToTrack(chords)
midi_file_out.write_Track(header[0], track, header[1], header[2])
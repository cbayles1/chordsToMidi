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

def calcInversionDistance(nc, prevnc):
    sum = 0
    
    for i in range(0, min(len(nc), len(prevnc))):
        now = nc[i].__int__()
        prev = prevnc[i].__int__()
        
        sum += abs(now - prev)
        
    return sum

def inverter(nc, prevnc, amtForLoops, forLoopIndex):
    if forLoopIndex >= amtForLoops:
        print(str(nc) + "\t" + str(prevnc) + "\t" + str(calcInversionDistance(nc, prevnc)))
    else:
        for i in range(-1,2):
            nc[forLoopIndex].from_int(nc[forLoopIndex].__int__() + 12 * i)
            print(nc[forLoopIndex])
            inverter(nc, prevnc, amtForLoops, forLoopIndex + 1)

def closestInversions(nc, prevnc):
    numNotes = min(len(nc), len(prevnc))
    inverter(nc, prevnc, numNotes, 0)
    
#    print(str(a) + "\t" + str(prevnc) + "\t" + str(calcInversionDistance(a, prevnc)))
    
    #for i in range(nc[0] - 12, nc[0] + 12, 12):
    #    for j in range(nc[1] - 12, nc[1] + 12, 12):
    #        for k in range(nc[2] - 12, nc[2] + 12, 12):
    #            etc etc ...   
    
    #for note in nc:
    #    a = nc
    #    for i in range(3): #TODO: CHANGE FROM 3
    #        print(str(a) + "\t" + str(prevnc) + "\t" + str(calcInversionDistance(a, prevnc)))
    #        a = mchords.invert(a) #TODO: ISN'T WILLING TO DEVIATE FROM ORIGINAL PITCHES, IT JUST SHUFFLES
    #        a[2].octave_up() #TODO: GO DOWN TOO
    #    print()
            
    return nc

def chordToNC(chord):
    notes = mchords.from_shorthand(chord)
    return NoteContainer(notes)

def chordsToTrack(chords, addRoots=True):
    t = Track()
    for i in range(0, len(chords)):
        
        chord = chords[i]
        nc = chordToNC(chord)
        
        if i > 0:
            nc = closestInversions(nc, chordToNC(chords[i-1]))
        
        root = getRoot(chord)
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
import re
from mingus.containers import Track
from mingus.containers import Bar
from mingus.containers import NoteContainer
from mingus.containers import Note
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

def closestInversion(nc, prevnc):

    def generate_combinations(positions):
        n = len(positions)

        all_combinations = []
        current_combination = [0] * n

        def generate_combinations_recursive(position):
            if position == n:
                all_combinations.append(list(current_combination))
                return

            values = positions[position]
            for value in values:
                current_combination[position] = value
                generate_combinations_recursive(position + 1)

        generate_combinations_recursive(0)
        return all_combinations

    def noteNumsToNoteContainer(nums):
        arr = []
        for note in nums:
            new = Note()
            new.from_int(note)
            arr.append(new)
            
        nc = NoteContainer()
        nc.add_notes(arr)
        return nc
 
    def calcInversionDistance(nc, prevnc):
        total_distance = 0
        num_pairs = 0

        for note1 in nc:
            for note2 in prevnc:
                distance = abs(note1 - int(note2))
                total_distance += distance
                num_pairs += 1

        if num_pairs > 0:
            avg_distance = total_distance / num_pairs
        else:
            avg_distance = 0

        return avg_distance
 
    def oldCalcInversionDistance(nc, prevnc):
        sum = 0
        
        for i in range(0, min(len(nc), len(prevnc))):
            now = nc[i]
            prev = int(prevnc[i])
            
            sum += abs(now - prev)
            
            print("i: " + str(i))
            print("Now: " + str(now))
            print("Prev: " + str(prev))
        
        print("Sum: " + str(sum)) 
        return sum

    options = [[int(note) - 12, int(note), int(note) + 12] for note in nc]
    combinations = generate_combinations(options)
    
    best = combinations[0]
    for combo in combinations:
        a = calcInversionDistance(combo, prevnc)
        b = calcInversionDistance(best, prevnc)
        if calcInversionDistance(combo, prevnc) < calcInversionDistance(best, prevnc):
            best = combo
    
    return noteNumsToNoteContainer(best)

def chordToNC(chord):
    notes = mchords.from_shorthand(chord)
    return NoteContainer(notes)

def chordsToTrack(chords, addRoots=True):
    t = Track()
    for i in range(0, len(chords)):
        
        chord = chords[i]
        nc = chordToNC(chord)
        
        #if i > 0:
        #    nc = closestInversion(nc, chordToNC(chords[i-1]))
        
        print(nc)
        
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
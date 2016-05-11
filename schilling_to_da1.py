from __future__ import print_function

min_num_fixations = 2 # drop trials that end up with fewer than this # of fixations

### first, figure out how long each word in schilling is
lengths = {} # lengths[item][wordnum]
words = {} #words[item][wordnum]

with open('schilling_human.txt') as rf:
    for linenum, line in enumerate(rf):
        line = line.rstrip('\n')
        lengths[linenum+1] = {}
        words[linenum+1] = {}
        for wordnum, word in enumerate(line.split()):
            lengths[linenum+1][wordnum+1] = len(word)
            words[linenum+1][wordnum+1] = word

region_starts = {} #region_starts[item][wordnum]
for item in xrange(1,48+1):
    region_starts[item] = {}
    for wordnum in xrange(1, len(lengths[item])+1):
        if wordnum==1:
            region_starts[item][wordnum] = 0
        if wordnum==2:
            region_starts[item][wordnum] = lengths[item][wordnum-1]
        if wordnum>2:
            prevstart = region_starts[item][wordnum-1]
            prevlen = lengths[item][wordnum-1]
            region_starts[item][wordnum] = prevstart+prevlen+1

### now, grab fixation info
fixations = {} # fixations[subject][fixnum] = (wordnum, letternum, dur)
for subject in xrange(1,31):
    with open('trace/TRACE' + str(subject)+ '.txt') as rf:
        fixations[subject] = {}
        item = 0
        wordnum = 0
        for line in rf:
            line = line.rstrip('\x1a')
            line = line.split()
            if len(line)==6: # heading
                item = int(line[3])
                wordnum = 1
                fixations[subject][item] = {}
            if (len(line)-1) % 3 == 0: # fixation
                word = line[0]
                known_word = words[item][wordnum]
                if (word <> known_word[:len(word)]):
                    print("We have a problem!")
                    print("word", word)
                    print("words", known_word)
                fixes = line[1:]
                numfixations = len(fixes)/3
                for i in xrange(numfixations):
                    fixnum = int(fixes[i*3])
                    letternum = int(fixes[i*3+1])
                    if letternum > lengths[item][wordnum]:
                        print("We have a length problem!")
                    dur = int(fixes[i*3+2])
                    fixations[subject][item][fixnum] = (wordnum, letternum, dur)
                wordnum += 1

### clean up fixations (get rid of initial fixations mid-sentence)
### we'll do this by removing any initial between-word regressions
### and also leave a record of which trials this affected
with open('funky_trials.txt', 'w') as funky_record:
    funky_record.write('subject\titem\tisFunky\n')
    for subject, subfixes in fixations.iteritems():
        for item, itemfixes in subfixes.iteritems():
            fixnums = itemfixes.keys()
            fixnums.sort()
            while((len(fixnums) >= 2) and (itemfixes[fixnums[0]][0] > itemfixes[fixnums[1]][0])):# identify between-words regressions
                fixnums = fixnums[1:]
            if len(fixnums)==len(itemfixes.keys()):
                funky_record.write(str(subject)+'\t'+str(item)+'\t'+'F\n')
            else:
                funky_record.write(str(subject)+'\t'+str(item)+'\t'+'T\n')
                # now drop those fixations from itemfixes
                for fixnum in itemfixes.keys():
                    if not (fixnum in fixnums):
                        del itemfixes[fixnum]
                
### finally, make da1 files
for subject in xrange(1,30+1):
    with open('da1/TRACE' + str(subject) + '.da1', 'w') as wf:
        last_item = 48
        if subject==15:
            last_item = 38 # this subject doesn't have all the data for some reason
        for item in xrange(1,last_item+1):
            fixnums = fixations[subject][item].keys()
            fixnums.sort()
            fixes = []
            time = 0
            for fixnum in fixnums:
                fix = fixations[subject][item][fixnum]
                wordnum = fix[0]
                letternum = fix[1]
                dur = fix[2]
                if wordnum == 1: ######## The first letter of the first word of a sentence has a position of 0 in the sentence, but a position of 1 in the word. Here we calculate the position in the sentence. 
                    x = letternum - 1
                else:
                    x = letternum + region_starts[item][wordnum]
                y = 0
                t1 = time
                t2 = time + dur
                fixes.append([str(x), str(y), str(t1), str(t2)])
                time = t2
            totaltime = time
            numfixes = len(fixes)
            if numfixes < min_num_fixations:
                print("Dropping subject %s item %s for having only %s fixations" % (subject, item, numfixes))
                continue
            wf.write('\t'.join([str(item), '1', str(item), str(totaltime), '0', '0', '0', str(numfixes)]))
            for fix in fixes:
                wf.write('\t'+'\t'.join(fix))
            wf.write('\n')

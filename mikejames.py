import numpy as np, os, sys, csv
NMAIN = int(sys.argv[2]) if len(sys.argv)>2 else 17
PRE2023 = False

print (' ###### Usage: python mikejames.py csv-file N ########## ')
print (' N is an optional argument; default is 17, decrease if you find text too wide for page')

def mark2string (mark):
    if 'R' in mark and not '_' in mark:  # R in some marks without underscore in 2022
        mark = mark.replace('R','_R')
    zmksplit = mark.split('_',1)
    zm_mark,zm_sub = zmksplit[0],''
    if len(zmksplit)>1:
        zm_sub=zmksplit[1]
    mstring = zm_mark if zm_mark!='100' else '{\\scriptsize 100}'
    if zm_sub!='':
        mstring += '{\\tiny $_{\\rm %s}$}'%zm_sub.replace('_','').lower()
    return mstring

def newmark2string (mark,subs):
    if subs=='':
        return mark
    return mark+'{\\tiny $_{\\rm %s}$}'%subs

def write_headers (fo,stable,headers):
    fo.write('\\begin{tabular}{p{36mm}')
    for i in range(1,stable.shape[1]):
        fo.write('l')
    fo.write('}\n')
    for i in range(len(headers)-1):
        fo.write('\\rot{%s} &'%headers[i])
    fo.write('\\rot{%s} \\\\\n'%headers[-1])

def shorten (s):     # strings to replace with other strings
    repl = ['ACTV','REVW','BSCHONS','MPHYS','MMATH&PH','ERASMUS','&','#',\
            'MA8','MA9','XN','MA0','RWF','MC3','%','RYOA','ROF','CERTHE',\
            'DIPHE','SR3']
    rwith = ['A','R','B','M','MM','E','','\#','8','9','N','0','F','3','\%',\
             'O','O','C','D','S3']
    for i in range(len(repl)):
        if repl[i] in s:
            return s.replace(repl[i],rwith[i])
    return s

# read all the data in one large array

data = np.array([])
fi = sys.argv[1] if len(sys.argv)>1 else 'yr1.csv'
csv_reader = csv.reader(open(fi))
for row in csv_reader:
    if not len(row):
        continue
    try:
        data = np.vstack((data,row))
    except:
        data = np.copy(row)

# Find a line with 'Name' in one of the columns - the assumption is that
# this line tells us the headers, and that students are subsequent lines
# where this column is non-zero

iskeyline = False
for i in range(len(data)):
    if ''.join(data[i]).count('Name'):
        print ('Found the columns key line %d'%i)
        iskeyline = True
        break

if iskeyline:
    keyline = i
else:
    print('Failed to find a line with Name + unit descriptions')
    exit(0)

ncol = np.argwhere(['Name' in x for x in list(data[keyline])])[0][0]
brow = np.ravel(np.argwhere([len(x)>3 for x in list(data[:,ncol])]))
brow = brow[brow>keyline][0]
erow = np.ravel(np.argwhere([len(x) for x in list(data[:,ncol])]))[-1]
acourses = np.array([],dtype='str')
pcourses = np.array([],dtype='str')

# find columns with unit data (labelled 'Unit '), name, and first and
# last rows with student names (assuming no others have anything in Name col)
# Failing that, search the whole array for columns containing ( and )

ucols = np.ravel(np.argwhere(['Unit ' in x for x in list(data[keyline])]))
if len(ucols)<2:
    print('Did not find more than two columns with marks in this line, trying first student row')
    ucols = np.array([],dtype='int')
    for i in range (brow,erow,2):
        for j in range (len(data[i])):
            if '(' in data[i,j] and ')' in data[i,j]:
                ucols = np.append(ucols,j)
    ucols = np.sort(np.unique(ucols))
                

print ('Found courses in columns: ',ucols)
if np.mean(np.gradient(ucols))<1.5:   # should be 1 for old, 2 for new
    PRE2023 = True
for i in range(brow,erow,2):
    for j in ucols:
        if data[i,j]=='':
            continue
        data[i,j]=data[i,j].split()[0].split('(')[0]  # remove e.g. (10)
        if data[i+1][j]!='':
            if data[i,j][:4]=='PHYS':                 # no. PHYS courses
                pcourses = np.append(pcourses,data[i,j])
            else:
                acourses = np.append(acourses,data[i,j])  # no. other courses

courses = np.hstack((np.sort(np.unique(pcourses)),np.sort(np.unique(acourses))))
course_entries = np.zeros(len(courses))
for i in range(len(courses)):
    pacourses = np.hstack((pcourses,acourses))
    course_entries[i] = len(pacourses[pacourses==courses[i]])

minmain = np.sort(course_entries)[::-1][NMAIN] + 1
ismain = courses[course_entries>=minmain]
print('--->',ismain)
isnotmain = courses[course_entries<minmain]
headers = np.hstack((['Name'],ismain,['Other'],shorten(data[keyline,ucols[-1]+2:])))

# fill the latex table

ssiz = np.array([],dtype='int')
for srow in range(brow,erow,2):
    s = []
    if ',' in data[srow,ncol]:
        data[srow,ncol] = ' '.join(data[srow,ncol].split(',')[::-1]).lstrip()
    if len(data[srow,ncol])>20:
        s.append(shorten('{\\scriptsize '+data[srow,ncol]+'}'))
    else:
        s.append(shorten(data[srow,ncol]))
    # main block of marks. Have to distinguish the case where comments
    # are in separate columns rather than Unit columns (2023-) and in
    # subscripts in each Unit column (-2022).
    for i in range(len(ismain)):
        try:
            idx = np.argwhere(data[srow]==ismain[i])[0][0]
            if PRE2023:          # comments with mark
                s.append(shorten(mark2string(data[srow+1][idx])))
            else:                # comments in separate columns
                s.append(shorten(newmark2string(data[srow+1][idx],data[srow+1][idx+1])))
        except:
            s.append('')
    isanynotmain,sthis = 0,''
    # block of marks for less popular courses
    for i in range(len(isnotmain)):
        if isnotmain[i] in data[srow]:
            idx = np.argwhere(data[srow]==isnotmain[i])[0][0]
            if data[srow+1,idx]=='':
                continue
            if not isanynotmain:
                sthis = '{\\small \\begin{tabular}[t]{l} '
            isanynotmain += 1
            sthis += (data[srow,idx]+':')
            if PRE2023:
                sthis += shorten(mark2string(data[srow+1][idx]))
            else:
                sthis += shorten(newmark2string(data[srow+1][idx],data[srow+1][idx+1]))
            sthis += '\\\\\n'
    if isanynotmain:
        sthis+='\\end{tabular}}'
    s.append(sthis)
    ssiz = np.append(ssiz,max(0,isanynotmain-1)+1) # rows in table = 1 plus 1 for each extra>1

    # final block

    for i in range(len(data[srow])-(ucols[-1]+2)):
        sprint = '{\\scriptsize '+data[srow,ucols[-1]+2+i]+'}'
        sprint = shorten(sprint)
        s.append(sprint)
    try:
        stable = np.vstack((stable,s))
    except:
        stable = np.copy(s)

froot = fi.split('.')[0]
fo = open(froot+'.tex','w')
fo.write('\\documentclass{article}\n')
fo.write('\\usepackage{array,graphicx,booktabs,pifont,lscape}\n')
fo.write('\\textwidth 165mm\n\\textheight 240mm\n')
fo.write('\\oddsidemargin -20mm\n\\evensidemargin -20mm\n\\topmargin 1mm\n')
fo.write('\\newcommand*\\rot{\\rotatebox{90}}\n')
fo.write('\\pagestyle{empty}\n')
fo.write('\\begin{document}\n\\begin{landscape}\n')
lpage = 0
write_headers (fo,stable,headers)
for i in range(stable.shape[0]):
    for j in range(stable.shape[1]-1):
        fo.write('%s &'%stable[i,j])
    fo.write('%s \\\\\n'%stable[i,-1])
    lpage += ssiz[i]
    if lpage>=40:
        fo.write('\\end{tabular}\n\n')
        write_headers (fo,stable,headers)
        lpage=0
fo.write('\\end{tabular}\n\\end{landscape}\n\\end{document}\n')
fo.close()
os.system('pdflatex '+froot)
os.system('rm '+froot+'.aux;rm '+froot+'.log')

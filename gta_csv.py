#
#  Turns Faculty spreadsheet into a readable latex table
#  Start with two csv files from the preferences and skills version of the
#  spreadsheet (written with SAVE AS csv and all defaults)
#
# 2023-2024 version
import numpy as np,os,sys
import csv

GTAPREFS = 'gta-prefs.csv'
GTASKILLS = 'gta-skills.csv'
#       You may need to change these depending on format of the csv files from the xlsx
PID,PNAME1,PNAME2,PDEPT,PGROUP = 1,2,3,5,6   # column numbers in the pref file
PDUTY,PINT = 0,8                             # cols describing duty/interest in prefs
SID,SNAME1,SNAME2,SDEPT,SGROUP = 2,3,4,6,7   # column numbers in the skills file
SSKILL,SLEVEL = 0,1                          # cols describing skill/levell in skills
                                             # (These changed 9/8/22 in the xlsx)
NUMPG = 30          # Number of entries per page of output PDF
EXCLUDE_MATHS = True    # to remove anyone who's said they want maths tutorials
#  Things below this shouldn't need changing for the program to work:
#  adjust the arrays below 'columns' for desired pdf table format.

try:
    gta_maths = np.loadtxt('gta_maths',delimiter=';',dtype='str')
except:
    gta_maths = []

def isgta (a,gta_id):
    for igta,gta in enumerate(a):
        if gta['gta_id'] == gta_id:
            return igta
    return -1

a=[]
#   Process preferences first - create array of dictionaries, one
#   entry per GTA and populate it with keys representing courses they
#   could teach
with open(GTAPREFS,mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        if row[PID]=='SPOT ID':
            continue
        # Add entry in main array if not present
        if isgta(a,row[PID])!=-1:   # present already
            pass
        else:
            if row[PNAME1]+' '+row[PNAME2] in gta_maths and EXCLUDE_MATHS:
                continue
            a.append(dict(gta_id=row[PID]))
            a[len(a)-1]['name']=row[PNAME1]+' '+row[PNAME2]
            a[len(a)-1]['dept']=row[PDEPT][:4]
            a[len(a)-1]['group']=row[PGROUP].replace('&','\&').replace('#','').replace('Group','').replace('group','')[:30]
        igta = isgta(a,row[PID])
        a[igta][row[PDUTY]] = row[PINT]

# Next the skills

with open(GTASKILLS,mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        if row[SID]=='SPOT ID':
            continue
        if isgta(a,row[SID])!=-1:   # present already
            pass
        else:
            if row[SNAME1]+' '+row[SNAME2] in gta_maths and EXCLUDE_MATHS:
                continue
            a.append(dict(gta_id=row[SID]))
            a[len(a)-1]['name']=row[SNAME1]+' '+row[SNAME2]
            a[len(a)-1]['dept']=row[SDEPT][:4]
            a[len(a)-1]['group']=row[SGROUP].replace('&','\&').replace('#','').replace('Group','').replace('group','')[:30]
        igta = isgta(a,row[SID])
        a[igta][row[SSKILL]]=row[SLEVEL]

# then write the table - adjust this array for whatever columns are interesting

columns = ['gta_id','name','dept','group','PHYS10180','PHYS20180',\
           'PHYS30180','PHYS20161','Programming: Python','Programming: C++',\
           'Aptitude to teach nuclear','Aptitude to teach electronics',\
           'Prefer/happy to work in electronics lab']

# for each column in the above array, write the header...

colhead = ['ID','Name','Dept','Group','\\rotatebox{90}{PHYS10180}',\
           '\\rotatebox{90}{PHYS20180}',\
           '\\rotatebox{90}{PHYS30180}',\
           '\\rotatebox{90}{PHYS20161}',\
           '\\rotatebox{90}{Python}',\
           '\\rotatebox{90}{C++}',\
           '\\rotatebox{90}{Nuclear}',\
           '\\rotatebox{90}{Electronics}',\
           '\\rotatebox{90}{Electronics}']

# ... and the latex table type

coltype = ['c','p{55mm}','c','p{70mm}','c','c','c','c','c','c','c','c','c','c']

# two arrays, one with the verbose thing, and a corresponding array with the
# compact entry for the tex table

entry = ['Not taught. Could teach.','Not taught. Strongly wish to teach.',\
         'Have taught. Wish to repeat.','Have taught. Prefer alternative.',\
         'Passing','Good','Phys','Not declared']
entry_alias = ['$\\circ$','$\\bullet$','$\\bullet$','$\\times$','$\\circ$',\
               '$\\bullet$','{\\bf Phys}','?']

fo = open('gta_table.tex','w')
fo.write('\\documentclass[12pt]{article}\n')
fo.write('\\textwidth 165mm\n')
fo.write('\\textheight 240mm\n')
fo.write('\\oddsidemargin -10mm\n')
fo.write('\\evensidemargin -10mm\n')
fo.write('\\topmargin -10mm\n')
fo.write('\\usepackage{lscape}\n')
fo.write('\\pagestyle{empty}\n')
fo.write('\\begin{document}\n')
fo.write('\\begin{landscape}\n')
fo.write('\\begin{tabular}{')
for c in coltype:
    fo.write(c)
fo.write('}\n')
for ic,c in enumerate(colhead):
    fo.write(colhead[ic])
    fo.write(' & ' if ic!=len(colhead)-1 else ' \\\\')
    
icou=0
for row in a:
    for column in columns:
        try:
            if row[column] in entry:
                fo.write(entry_alias[entry.index(row[column])])
            else:
                fo.write(row[column])
        except:
            pass
        fo.write(' & ')
    fo.write('\\\\\n')
    icou+=1
    if not icou%NUMPG:        # reached end of page, write another header
        fo.write('\\end{tabular}\n\n')
        fo.write('\\begin{tabular}{')
        for c in coltype:
            fo.write(c)
        fo.write('}\n')
        for ic,c in enumerate(colhead):
            fo.write(colhead[ic])
            fo.write(' & ' if ic!=len(colhead)-1 else ' \\\\')
    

fo.write('\\end{tabular}\n\\end{landscape}\n\\end{document}\n')
fo.close()

os.system('pdflatex gta_table')
os.system('rm gta_table.aux;rm gta_table.log')
print ('Finished - PDF should be in file gta_table.pdf')

#
#  Turns Faculty spreadsheet into a readable latex table
#  Start with two csv files from the preferences and skills version of the
#  spreadsheet (written with SAVE AS csv and all defaults)
#
import numpy as np,os,sys
import csv

GTAPREFS = 'gta-prefs.csv'
GTASKILLS = 'gta-skills.csv'
ID,NAME1,NAME2,DEPT,GROUP = 2,3,4,5,6   # column numbers in the csv files
NUMPG = 30          # Number of entries per page of output PDF
EXCLUDE_MATHS = True    # to remove anyone who's said they want maths tutorials
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
        if row[ID]=='SPOT ID':
            continue
        # Add entry in main array if not present
        if isgta(a,row[ID])!=-1:   # present already
            pass
        else:
            if row[NAME1]+' '+row[NAME2] in gta_maths and EXCLUDE_MATHS:
                continue
            a.append(dict(gta_id=row[ID]))
            a[len(a)-1]['name']=row[NAME1]+' '+row[NAME2]
            a[len(a)-1]['dept']=row[DEPT][:4]
            a[len(a)-1]['group']=row[GROUP].replace('&','\&').replace('#','').replace('Group','').replace('group','')[:30]
        igta = isgta(a,row[ID])
        a[igta][row[0]] = row[1]

# Next the skills

with open(GTASKILLS,mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        if row[ID]=='SPOT ID':
            continue
        if isgta(a,row[ID])!=-1:   # present already
            pass
        else:
            if row[NAME1]+' '+row[NAME2] in gta_maths and EXCLUDE_MATHS:
                continue
            a.append(dict(gta_id=row[ID]))
            a[len(a)-1]['name']=row[NAME1]+' '+row[NAME2]
            a[len(a)-1]['dept']=row[DEPT][:4]
            a[len(a)-1]['group']=row[GROUP].replace('&','\&').replace('#','').replace('Group','').replace('group','')[:30]
        igta = isgta(a,row[ID])
        a[igta][row[0]]=row[1]

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

coltype = ['c','p{60mm}','c','p{70mm}','c','c','c','c','c','c','c','c','c','c']

# two arrays, one with the verbose thing, and a corresponding array with the
# compact entry for the tex table

entry = ['Not taught. Could teach.','Not taught. Strongly wish to teach.',\
         'Have taught. Wish to repeat.','Have taught. Prefer alternative.',\
         'Passing','Good','Phys']
entry_alias = ['$\\circ$','$\\bullet$','$\\bullet$','$\\times$','$\\circ$',\
               '$\\bullet$','{\\bf Phys}']

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

#
#  Converts CSV output from google forms to tex and thence pdf
#  Assumes input file has '.csv' suffix
#
import os,sys,numpy as np,re
#infile = sys.argv[1] if len(sys.argv)>1 else 'responses.csv'
#tabstring = sys.argv[2] if len(sys.argv)>2 else 'lp{40mm}p{40mm}llp{120mm}lllll'
infile = 'responses.csv'
tabstring = 'lp{40mm}p{40mm}llp{130mm}lllll'
outfile = infile.replace('.csv','.tex')
linesperpage = 25

# open files - note that csv files have \r\n for newline
f,fo = open(infile,newline='\r\n'), open(outfile,'w')
fo.write('\\documentclass[12pt]{article}\n\\parindent 0mm\n\\parskip 3mm\n\\usepackage{graphicx}\n\\usepackage[landscape]{geometry}\n\\evensidemargin -20mm\\oddsidemargin -20mm\n\\topmargin -30mm\n\\textwidth 170mm\n\\textheight 250mm\n\\pagestyle{empty}\n\\begin{document}\n\\scriptsize\n')
fo.write('\\begin{tabular}{%s}\n'%tabstring)
l = f.readlines()
f.close()
linecount = 0
for line in l:
    linecount += 1
    # remove commas between double quotes - clanky way by char
    # eliminate carriage returns and quotes in lines
    dowrite = True
    newline = ''
    for i in range(len(line)):
        if line[i] not in ['"','\n'] and \
           (dowrite or (not(dowrite) and line[i]!=',')):
            newline += line[i]
        else:
            newline += ' '
        if line[i]=='"':
            dowrite = not(dowrite)
    line = newline
    ll = line.split(',')
    for i in range(len(ll)):
        # file-dependent substitutions
        ll[i] = 'Lab' if ll[i]=='Lab demonstrating' else ll[i]
        ll[i] = 'Maths' if ll[i] == 'Maths tutorials' else ll[i]
        ll[i] = 'S1+S2' if ll[i] == 'Both S1 and S2' else ll[i]
        # Deal with & input by user to convert for tex table
        ll[i] = ll[i].replace('&','\&')
        if i==0:
            ll[i] = ll[i][:5]
        n=fo.write(ll[i])
        n=fo.write('&' if i<len(ll)-1 else '\\\\\n')
    if linecount == linesperpage:
        linecount = 0
        fo.write('\\end{tabular}\n\\begin{tabular}{%s}\n'%tabstring)

fo.write('\\end{tabular}\n\\end{document}\n')
fo.close()

os.system('pdflatex '+infile.split('.csv')[0])
os.system('rm '+infile.replace('.csv','.aux'))
os.system('rm '+infile.replace('.csv','.log'))


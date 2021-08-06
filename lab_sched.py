import numpy as np,os,time,sys
#    syntax: python lab_sched.py [lab-people-file] [iscovid]
#           use python lab_sched.py lab_people 1 (or lab_people_off 2)
NWEEK = 24
def consolidate (infile, outfile):
    f=open(infile)
    fo=open(outfile,'w')
    oldname='';oldfields = ''
    while True:
        i = f.readline()
        if i:
            name = ' '.join(i.split()[:len(i.split())-2]).strip()
#            name = i.split('[')[0].strip()
            this_class = i.split()[-1]
            fields = i.split()[-2]
        else:
            name = 'ZZZZZZZ'
        if name != oldname:
            if oldname=='':
                fo.write('Name,T,1,2,3,4,5,6,7,8,9,10,11,12,1,2,3,4,5,6,7,8,9,10,11,12\n')
            else:
                fo.write ('%s '%(oldname))
            for j in range(NWEEK):
                try:
                    sys.stdout.write('%d '%intfields[j])
                    fo.write(',%d'%intfields[j])
                except:
                    pass
            fo.write('\n')
            intfields = np.zeros(NWEEK,dtype='int')
            for j in range(NWEEK):
                print(fields,j)
                intfields[j] += int(fields[j])
            oldname = name; oldfields=fields
        else:
            if oldfields!='':
                oldfields = '%s'%(int(oldfields)+int(fields))
                oldfields = oldfields.zfill(NWEEK)
                for j in range(NWEEK):
                    intfields[j] += int(fields[j])
                    sys.stdout.write('%d '%intfields[j])
#                fo.write('\n')
        if not i:
            break
                    
    fo.close(); f.close()

ut=time.ctime()
iscovid = 0      # iscovid = 0 if vaccine=True
if len(sys.argv)>2:
    iscovid = int(sys.argv[2])
f = open('lab_skeleton_CV%d.tex'%iscovid if iscovid else 'lab_skeleton.tex')
fo=open('labdem.tex','w')
for i in f:
    if '#TIME' in i:
        i=i.replace('#TIME',ut)
    if i[0]!='%':
        if i[:3]=='END':
            break
        fo.write('%s'%i)
    else:
        psiz = '170' if i[:6]=='%MATHS' else '30'
        if iscovid and i[:5] in ['%S1Y3','%S2Y3']:
            psiz = '100'
        fo.write('\\begin{tabular}{p{'+psiz+'mm}}\n')
        fp=open('lab_people' if len(sys.argv)<2 else sys.argv[1])
        dowrite=False
        for j in fp:
            if j[0]=='#':
                continue
            if dowrite and len(j)>1:
                fo.write('%s\\\\\n'%j.strip())
            if j[0]=='%':
                dowrite=False
                if (j.split())[0]==(i.split())[0]:
                    dowrite=True

        fp.close()
        fo.write('\\end{tabular}\n')
f.close()

import lab_distr
fo.write('\\begin{verbatim}\n')
fi=open('lab_alloc')
for i in fi:
    fo.write(i)
fi.close()
fo.write('\\end{verbatim}\n')
fo.write('\\end{document}\n')
fo.close()
os.system('pdflatex labdem')
os.system('rm labdem.aux')
os.system('rm labdem.log')
#os.system('acroread labdem.pdf')

# write the contract sheet

import lab_contract_data
contract = lab_contract_data.lab_contract_data()

f = open('lab_people')
fo = open('lab_contracts.temp1','w')
for i in f:  # find names of GTAs for contract generation
    isdoingweeks = [True]*25
    # process only names without dots; exclude section headings or comments
    if not len(i.strip()) or '.' in i or '\\bf' in i or "{" in i or i[0]=='#':
        continue
    print ('Processing name:',i)
    if '(w' in i:    # take things like (w1-5) out of names and adjust contract hours
        weeks = np.asarray(i.split('(w')[1].split(')')[0].split('-'),dtype='int')
        print (weeks,weeks[0],weeks[1])
        i = i[:i.index('(')].rstrip()
        # only works for S1 here!! and requires exact formatting Joe Bloggs (w7-12)
        for j in range(25):
            if j<weeks[0] or j>weeks[1]:
                isdoingweeks[j] = False
    if i[0]=='%':   # start of a different lab
        if i[1:6]=='MATHS':
            break
        this_class = i[1:]
        try:
            test_current = i[1:].strip()
            junk =  contract[test_current]
            current = test_current
        except:
            pass
        continue
    ctemp = contract[current]+'XE' if 'XE' in i else contract[current]
    ctemp = list(ctemp[0])
    cwrite=''
    print (ctemp,isdoingweeks)
    for j in range(25):
        cwrite += (ctemp[j] if isdoingweeks[j] else '0')
    if 'XE' in i:
        fo.write('%s %s %s'%(i.strip().strip('(XE)'), cwrite,this_class))
    else:
        fo.write('%s %s %s'%(i.strip(), cwrite,this_class))

fo.close()
f.close()
os.system ('sort lab_contracts.temp1 >lab_contracts.temp2')
os.system ('uniq lab_contracts.temp2 >lab_contracts.temp3')
consolidate ('lab_contracts.temp3','lab_contracts.csv')
os.system ('rm lab_contracts.temp1; rm lab_contracts.temp2;rm lab_contracts.temp3')

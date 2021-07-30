import numpy as np,os,glob
f=open('lab_people')
for i in f:
    if len(i)<3 or any(x in i for x in '%{.'):
        continue
    i=i.strip('\n')
    try:
        new = i.split()[0]+' '+i.split()[1]
    except:
        continue
    try:
        b=a[0]
    except:
        a=np.array([new])
    if not (new in a):
        a = np.append(a,new)

f.close()
try:
    a=np.sort(a)
    fo = open('lab_alloc','w')
    for i in a:
        fo.write('%s '%i)
        f=open('lab_people')
        for j in f:
            if len(j)<3 or any(x in j for x in '{.'):
                continue
            if j[0]=='%':
                thissubj = j[1:].strip('\n')
            try:
                new = j.split()[0]+' '+j.split()[1]
            except:
                continue
            if i==new:
                fo.write('%s '% thissubj)
        fo.write('\n')
    fo.close()
except:
    print ('Warning: no lab contracts produced (no PGs)?')
        


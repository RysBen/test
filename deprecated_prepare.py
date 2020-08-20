# (deprecated) mkdir, print cmd, 201910

import os
path="E:\\clinical\\"
for line in open('list.txt'):
    line=line.strip().split('\t')
    if line[2]=='':
        print("cd `chd %s`; echo 'Main_Dir'; lp; cd report; echo 'lims'; lims" %(line[3]))
        print('chd %s' %(line[3]))
        fn=line[3]
        panel=line[0]
        if panel=="CT_DNA_800a063":
            panel_fn="825"
        elif  panel=="CT_DNA_063_18":
            panel_fn="18"
        elif  panel=="CT_DNA_184_180":
            panel_fn="180"
        else:
            panel_fn=""
        os.mkdir(path+fn+'-'+panel_fn)
    else:
        print('tn %s %s' %(line[3],line[2]))
        fn=line[3]
        panel=line[0]
        if panel=="CT_DNA_800a063":
            panel_fn="825"
        elif  panel=="CT_DNA_063_18":
            panel_fn="18"
        elif  panel=="CT_DNA_184_180":
            panel_fn="180"
        else:
            panel_fn=""     
        os.mkdir(path+fn+'-'+panel_fn)
    print("************\n")

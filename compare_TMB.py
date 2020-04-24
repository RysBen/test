import os
import glob
import subprocess
import re
import sys

def main():
    list=sys.argv[1]
    for tsample in open(list):
	print tsample
        filvar=glob.glob("/clinical/public/*panel*/*"+tsample+"*/report/*ct.filvar.xls")[0]

        rdir=os.path.dirname(filvar)
        syn=glob.glob(rdir+"/*synonymous.xls")[0]
        syn_RowNum=sum(1 for r in open(syn))

        tmb=subprocess.Popen(["ls /clinical/public/*panel*/*W053461T*/report/TMB:*|cut -d':' -f2"],shell=True,stdout=subprocess.PIPE).communicate()[0].strip()
	report2b=glob.glob(rdir+"/report2b.sh")[0]
	panel=subprocess.Popen(["grep panel825_tmb_lh %s |cut -d' ' -f4" %(report2b)],shell=True,stdout=subprocess.PIPE).communicate()[0].strip()

        if syn_RowNum > 0:
	    filvar_sl=compare(filvar,syn)
            tmbnew=cal_tmb(filvar_sl,panel)
            print rdir,tmb,tmbnew
        else:
            print lib,"syn is empty"
    
def compare(filvar,syn):
    syn_D={}
    filvar_D={}
    filvar_sl=[]
    filvar_fl=[]

    for lf in open(filvar):
        if not ls.startswith("#"):
	    lf=lf.strip()
	    lfs=lf.split('\t')
	    keyf=lfs[4]+'_'+lfs[5]+'_'+lfs[9]+'_'+lfs[10]
	    filvav_D[keyf]=lf

    for ls in open(syn):
        ls=ls.strip()
	lsl=ls.split('\t')
        keys=ls1[0]+'_'+lsl[1]+'_'+lsl[2]+'_'+lsl[3]
        syn_D[keyf]=ls

    for k,v in filvav_D.items():
	if k not in syn_D.keys():
	    filvar_sl.append(v)
	else:
	    filvar_fl.append(v)
    
    return filvar_sl

def cal_tmb(filvar_sl,panel):
    num=len(filvar_sl)
    if panel == 'panel825':
        tmb_value = float(num)/float(2.1)
    if re.search('panel825plus',panel):
        tmb_value = float(num)/float(2.13)
    if panel == 'panel825-m':
        tmb_value = float(num)/float(2.11)
    if panel == 'panel825-ct' or re.search('panel825-63',panel):
        tmb_value = float(num)/float(0.93)
    if re.search('panel179-',panel):
        tmb_value = float(num)/float(0.3)
    if re.search('panel180-',panel):
        if re.search("CSF",file):                   
            num = 0 
            for e in filvar_sl:
                    freq = float(e.split("\t")[24])
                    if freq > 0.005:
                        num+=1  
        else:
            pass 
        tmb_value = float(num)/float(0.3)
    if re.search('panel190-',panel):
        tmb_value = float(num)/float(0.4)
    if re.search('WES',panel):
        tmb_value = float(num)/float(30.4)
    return tmb_value

if __name__ == "__main__":
    main()

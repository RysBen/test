import glob
import sys

seqQC={}
seqQC_nf=[]
seqQC_fail=[]

for l in open('list','r'):
    l=l.strip().split('\t')
    pn=l[0]
    sy=l[1]
    i=l[2]
    print pn,sy,i
    seqQC_pattern="/clinical/*/*panel*/*"+i+r"*/qc_report_seq/"+i+"_library_QC_report.xls"
    seqQC_path=glob.glob(seqQC_pattern)
    #print i,seqQC_path
    if seqQC_path != []:
        seqQC[i]=open(seqQC_path[0]).readlines()
    else:
        seqQC[i]=''
        seqQC_nf.append(i)

# Newdemand: use data storing in cold backup
for i in seqQC_nf:
    seqQC_path_cb=glob.glob("/biocluster/data/biobk/user_test/renshuaibing/seqQc_final/cb/"+i+"_library_QC_report.xls")
    if seqQC_path_cb != []:
        seqQC[i]=open(seqQC_path_cb[0]).readlines()

outxls=sys.argv[1]+r"/seqQC_out_"+sys.argv[1]+".xls"
print outxls

f=open(outxls,'w')
for l in open('list','r'):
    l=l.strip().split('\t')
    pn=l[0]
    sy=l[1]
    i=l[2]
    if i in seqQC.keys() and seqQC[i] != '':
	f.write(sy+'_'+i+'\n')
	f.writelines(seqQC[i])
	f.write('\n')
    else:
	f.write(sy+'_'+i+"\tNotFindInClinicalOrColdBackup\n\n")
	seqQC_fail.append(i)
f.close()

print "======CannotFindFinal======"
fail=set(seqQC_fail)
print len(fail)
for x in sorted(list(fail)):
    print x

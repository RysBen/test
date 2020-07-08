import sys
import glob
import re

#{KRAS:Gly12Asp 12_25398284_C_T, NRAS:Gly12Asp 1_115258747_G_A, EGFR:Ser768Ile:7_55249005_G_[T,A]}
p2v={"Thr790Met":"7_55249071_C_T", "19del":"7_552424[6-7][0-9]", "Arg132Cys":"2_209113113_G_A", "Arg132Ser":"2_209113113_G_T", "Arg140Gln":"15_90631934_C_T",
     "Arg249Ser":"17_7577534_C_A", "Cys797Ser":"7_55249092_G_C", "Gln61Arg":"1_115256529_T_C", "Glu542Lys":"3_178936082_G_A", "Gly12Ala":"12_25398284_C_G",
     "Gly12Asp":"12_25398284_C_T|1_115258747_C_T", "Gly12Cys":"12_25398285_C_A", "Gly12Ser":"12_25398285_C_T", "Gly12Val":"12_25398284_C_A", "Gly13Asp":"12_25398281_C_T",
     "Gly719Ala":"7_55241708_G_C", "Gly719Cys":"7_55241707_G_T", "Gly719Ser":"7_55241707_G_A", "His1047Arg":"3_178952085_A_G", "His1047Leu":"3_178952085_A_T",
     "Leu858Arg":"7_55259515_T_G", "Leu861Gln":"7_55259524_T_A", "Ser768Ile":"7_55249005_G_[AT]", "Val600Glu":"7_140453136_A_T", "Glu545Lys":"3_178936091_G_A"}

def read_support(sinfo):
	stmp = re.split('\|',sinfo)
	pos = re.split(':',stmp[0])[1]
	ins_oriention = stmp[1][:2]
	insertsize = stmp[1][2:]
	tag = re.split('#',stmp[2])[0]
	return pos,ins_oriention,insertsize,tag

def compare_support(sinfo1,sinfo2):
	pos1,ins_oriention1,insertsize1,tag1 = read_support(sinfo1)
	pos2,ins_oriention2,insertsize2,tag2 = read_support(sinfo2)
	if ins_oriention1 != ins_oriention2[::-1]:  #+- ~ -+
		return False
	elif insertsize1 != insertsize2:
		return False
	elif tag1 != '+'.join(re.split('\+',tag2)[::-1]):
		return False
	elif pos1 not in [str(int(pos2)-1),pos2,str(int(pos2)+1)]:
		return False
	else:
		return True

def vcf_key_compare(path,ddpcr_key):
    for l in open(path):
        if not l.startswith('#'):
	    vcf_ll=l.strip().split('\t')
	    chr=vcf_ll[0]
	    pos=vcf_ll[1]
	    ref=vcf_ll[3]
	    alt=vcf_ll[4]
	    vcf_key=chr+'_'+pos+'_'+ref+'_'+alt
	    if re.findall(ddpcr_key,vcf_key):
	        #print "p2:",ddpcr_key,"findall",vcf_key
	        support_ll=vcf_ll[10].strip().split('support=')[1].split(',')
		duplex_num=0
		single_num=0
		for n in range(len(support_ll)):
                    support1 = support_ll[n]
		    for m in range(n+1,len(support_ll)):
			support2 = support_ll[m]
			if compare_support(support1,support2):
		            duplex_num += 1
			else:
			    single_num += 1
		return support_ll,duplex_num,single_num,len(support_ll)
    return ["na","na"],"na","na","na"

def main():
    infile=open(sys.argv[1])
    outfile=open(sys.argv[1]+"_out.xls",'a')
    for l in infile:
        ll=l.strip().split(',')
        tsample=ll[3]
        site=ll[5]
	key1=p2v[site]
	snp=glob.glob('/clinical/public/*panel*/*'+tsample+'*/var_seq/*snp.removed_dup.vcf')
	indel=glob.glob('/clinical/public/*panel*/*'+tsample+'*/var_seq/*indel.removed_dup.vcf')
	print "snp_path1:",snp
	if len(snp) == 0:
	    snp=glob.glob('/biocluster/data/biobk/user_test/renshuaibing/tasks/single_duplex_stat_202004/MergeVcf/'+tsample+'.snp.merge.vcf')
	    indel=glob.glob('/biocluster/data/biobk/user_test/renshuaibing/tasks/single_duplex_stat_202004/MergeVcf/'+tsample+'.indel.merge.vcf')
	    print "snp_path2:",snp
	if len(snp) != 0:
	    if key1 !=None:
                print key1
	        if site != '19del':
	  	    vcf_path=snp[0]
	        else:
		    vcf_path=indel[0]
	        support_ll, duplex_num, single_num, support_num=vcf_key_compare(vcf_path,key1)
	        #print "p5:final",tsample,site,duplex_num,single_num

	        ll.append(str(duplex_num))
	        ll.append(str(single_num))
	        ll.append(",".join(support_ll))
		ll.append(",".join(str(support_num)))

	        newline="\t".join(ll)
	        outfile.writelines(newline+'\n')
	    else:
                print "*********Key1 Not Found!Please Check the site in ddpcr or not*********"
	        outfile.writelines("\t".join(ll)+'not_find_key\t'+'\n')
	else:
	    outfile.writelines("\t".join(ll)+'not_find_vcf\t'+'\n')


if __name__ == "__main__":
    main()

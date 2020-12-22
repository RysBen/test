import click
from collections import Counter

def gcContent(seq,min,max):
	counters=Counter(seq)
	gc=counters['G']+counters['C']
	if gc < 3 or gc > 5:
		return 1
	else:
		return 0

def triplet(seq):
	tri=['A'*3,'T'*3,'C'*3,'G'*3]
	for i in tri:
		if i in seq: return 1
	return 0

def hanmming(seq1,seq2,min):
	count=0
	for a,b in zip(seq1,seq2):
		if a == b:
			count += 1
			if count > 4: return 1
	return 0

@click.command()
@click.option('--bf', help='the barcode file to check')
@click.option('--out', help='the barcode fil checkede')
@click.option('--gc_min', default=3, help='GC content min')
@click.option('--gc_max', default=5, help='GC content max')
@click.option('--dis_min', default=4, help='hamming distance min')
def main(bf,out,gc_min,gc_max,dis_min):
	seq0_l=[]
	seqt_l=[]
	seq1_l=[]
	with open(bf) as f:
		for line in f: seq0_l.append(line.strip())
	for i in range(len(seq0_l)-1):
		seq1=seq0_l[i]
		if gcContent(seq1,gc_min,gc_max): continue
		if triplet(seq1): continue
		for seq2 in seq0_l[i+1:]:
			if hanmming(seq1,seq2,min): seqt_l.append(seq2)
		seq1_l.append(seq1)
	print seqt_l,len(set(seqt_l))
	final=[ s1 for s1 in seq1_l if s1 not in seqt_l ]
	print final,len(final)
	with open(out,"w") as o:
		for i in final: o.write("%s\n" % i)

if __name__ == "__main__":
	main()

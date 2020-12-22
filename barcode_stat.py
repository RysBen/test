import sys
import pandas as pd
from itertools import combinations
from collections import Counter

xls=sys.argv[1]

def hanmmingDistance(seq1,seq2):
	count=0
	for a,b in zip(seq1,seq2):
		if a == b:
			count += 1
	return count

def main():
	#read input and transform d0
	df=pd.read_table(xls,header=None)
	d0=dict([(a,b) for a,b in zip(df[0],df[2])])

	#calculate hamming distance and store in d1
	d1={}
	for ka,kb in combinations(df[0],2):
		d1[(ka,kb)]=hanmmingDistance(d0[ka],d0[kb])

	#stat every sequence's hanmming distance and store in d2
	d2={}
	df2=pd.DataFrame(columns=['N'+str(i) for i in range(8,-1,-1)])
	for k0 in df[0]:
		for k1 in d1:
			if k0 in k1:
				d2.setdefault(k0,[]).append(d1[k1])
		counters=Counter(d2[k0]).items()
		for i in counters:
			df2.loc[k0,'N'+str(i[0])]=i[1]

	#result format
	df2=df2.fillna(0)
	df3=df.set_index(df[0]).join(df2)
	df3.rename(columns={0:'.',1:'.',2:'.'},inplace=True)
	df3.to_csv('barcode_stat_Rys.csv',index=0)

if __name__ == '__main__':
	main()

import pandas as pd
import os,sys

anno=sys.argv[1]
mut=sys.argv[2]

df1=pd.read_csv(mut,sep="\t")
df2=pd.read_csv(anno,sep="\t")

df_t=df2.iloc[:,1:27]
df_t['Chromosome']=df_t['Chromosome'].map("chr{}".format)
df_t['Exon_num']=df_t['Exon_num'].apply(lambda x: str(x).split('|')[0])
df_t.drop('GO_Molecular_Function',axis=1,inplace=True)
df_t['Tumor_mutant_frequency']=df_t['Tumor_mutant_frequency'].apply(lambda x: x*100)

df_t.rename(columns={'Refseq_mRNA_Id':'Refseq_transcript_ID', \
                     'Ensemble_mRNAID':'Ensemble_transcriptID'},inplace=True)
df=pd.concat([df1,df_t],axis=0)
df=df.reindex(columns=df1.columns)
df=df.fillna('.')

os.system("mv %s %s.bak" % (mut,mut))
df.to_csv(mut,sep="\t",index=0)

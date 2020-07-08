#masked

sample=$1
out=$2
gene_file=/yc/database/panel825-63_mutgene.txt

echo cp /cp/*panel*/*${sample}*/var_seq/*removed_dup.vcf . > ${out}/filter.sh

echo ##########################################################################################filter1 >> ${out}/filter.sh
echo python /rys/filter_flow/ctdna_filter_step1_test.py \
--input_vcf ${sample}.snp.removed_dup.vcf \
--false_position /ct181/database/false_positive.txt \
--read_support 4 \
--min_fre 0.001 \
--l_dis 30 \
--group_num \
--out_success ${sample}.snp.merge.support.vcf.step1.filted.vcf \
--out_fail ${sample}.snp.merge.support.vcf.step1.fail.vcf >> ${out}/filter.sh

echo python /rys/filter_flow/ctdna_filter_step1_test.py \
--input_vcf ${sample}.indel.removed_dup.vcf \
--false_position /ct181/database/false_positive.txt \
--read_support 4 \
--min_fre 0.001 \
--l_dis 30 \
--group_num \
--out_success ${sample}.indel.merge.support.vcf.step1.filted.vcf \
--out_fail ${sample}.indel.merge.support.vcf.step1.fail.vcf >> ${out}/filter.sh

echo "##########################################################################################combine" >> ${out}/filter.sh
echo python /ct181/combine_pos.py \
-s ${sample}.snp.merge.support.vcf.step1.filted.vcf \
-i ${sample}.indel.merge.support.vcf.step1.filted.vcf \
--snp_dis 3 \
--indel_dis 100 \
--out_file $sample.linked.step1.filted.vcf \
--genenome /REF/Homo_sapiens_assembly19.fasta >> ${out}/filter.sh

echo "##########################################################################################filter2" >> ${out}/filter.sh
echo sh /ct181/vcfTableAnnovar.sh $sample.linked.step1.filted.vcf >> ${out}/filter.sh

echo python /ct181/ctdna_filter_step2.py \
--input_vcf $sample.linked.step1.filted.vcf \
--input_annovar $sample.linked.step1.filted.vcf.hg19_multianno.txt \
--fre_human 0.01 \
--code_filter \
--out_success $sample.snp_indel.final.vcf \
--out_fail $sample.linked.step2.fail.vcf >> ${out}/filter.sh

echo "##########################################################################################anno,pgdx" >> ${out}/filter.sh
echo "awk '$1 == 7 && $2 == 55249063 && $4 == "G" && $5 == "A"' $sample.snp.merge.vcf >> $sample.snp_indel.final.vcf" >> ${out}/filter.sh

echo "cut -f 1-10 $sample.snp_indel.final.vcf > $sample.snp_indel.final.to_annotate.vcf" >> ${out}/filter.sh

echo python /ct/snpIndel_annotate.py \
-s $sample.snp_indel.final.to_annotate.vcf \
-t ctdna \
-o . \
-S $sample \
-c l \
-C L >> ${out}/filter.sh

echo "while read a b;do grep \$a $sample.annotate.xls |grep \$b >> $sample.annotate.consequence.filter.xls;done < /yc/database/synonymous_variant.xls" >> ${out}/filter.sh

echo sh /zn/T-CT_diff/PGDX/pipe_code/pgdxFilter.sh \
$sample.snp_indel.final.vcf \
$sample.annotate.consequence.filter.xls >> ${out}/filter.sh

echo "##########################################################################################db" >> ${out}/filter.sh
echo mkdir temp >> ${out}/filter.sh
echo python /yc/CTDNA/filterGene.py \
${sample}.annotate.consequence.filter.xls \
temp/${sample}.annotate.consequence.filter.xls \
$gene_file >> ${out}/filter.sh

echo "python /yc/CTDNA/filter_germline_ctdna.py -g /yc/CTDNA/germline_filter.xls \
-i temp/${sample}.annotate.consequence.filter.xls \
-t anno > temp/${sample}.filter1.xls" >> ${out}/filter.sh

echo python /zn/GermlineDatabase/pipe/dbFilter.py \
-a temp/${sample}.filter1.xls \
-o ${sample}.final.xls \
-d /zn/GermlineDatabase/data/GHfp.ctdna.json >> ${out}/filter.sh

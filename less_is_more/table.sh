# a field of fileA in a field of fileB or not
awk 'NR==FNR{a[$6];next}{if($6=="Start_position") $1="igv_flag" FS $1; else if($6 in a) $1="T" FS $1; else $1="F" FS $1}1' FS="\t" OFS="\t" ${final1} ${final} > ${out}/${f1_name}.igv

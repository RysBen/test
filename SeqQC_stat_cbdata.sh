for i in `cat list`;
do
seq_qc=`cat /clinical/DataColdBackup2019/CT_data/CT_backup_dataPath.txt| grep $i| grep qc_report_seq`
final=`cat /clinical/DataColdBackup2019/CT_data/CT_backup_dataPath.txt|grep report/${i}.final.xls`

if [ ! $seq_qc ];then
    echo $i > /dev/null
else
    echo $seq_qc >> cb_path_seqQc
fi

if [ ! $final ];then
    echo $i > /dev/null
else
    echo $final >> cb_path_final
fi
done

cat cb_path_seqQc cb_path_final >> cb_path
rm cb_path_seqQc cb_path_final

#mkdir cb
perl /biocluster/data/biobk/user_test/zhouyang/bin/tools/back_file_download.pl -i /biocluster/data/biobk/user_test/renshuaibing/seqQc_final/cb_path -od cb

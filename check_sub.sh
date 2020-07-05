#/bin/sh

lst=aro_list_$(date "+%H-%M-%S")
hand aro -n sxlj list > $lst

for i in `cat $1`
do
if [ ${i:0-1} = 'T' ];then
    cat $lst|grep -i $i|grep $2|grep -v 40g|grep sub|grep Succeeded >> ${1}_aro_subSucceed
else
    cat $lst|grep -i $i|grep sub|grep Succeeded >> ${1}_aro_subSucceed
fi
done

cut -d '-' -f2 ${1}_aro_subSucceed |tr a-z A-Z > ${1}_${2}_subSucceed
rm ${1}_aro_subSucceed

sort $1 ${1}_${2}_subSucceed ${1}_${2}_subSucceed|uniq -u > ${1}_${2}_subFailed

n1=`cat $1 | wc -l`
n2=`cat ${1}_${2}_subSucceed | wc -l`
n3=`cat ${1}_${2}_subFailed | wc -l`
echo -e "\033[7mCheck Results\033[0m"
echo -e "[1]Total: $n1 [2]Succeed: $n2 [3]May Failed: $n3 \n"

echo -e "\033[7mManually Check\033[0m"
for i in `cat ${1}_${2}_subFailed`
do
echo "hand aro -n sxlj list|grep -i $i"
done
echo

echo -e "\033[7mSubmit Command\033[0m"
echo "ls -lrt /hongshan/software/auto_submit/PC*sh"

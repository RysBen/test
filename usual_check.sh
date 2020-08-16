k8s=$1

hand ${k8s:-arg} -n sxlj list > ${k8s:-arg}.list.tmp

for i in `cat usual`
do
  grep -i $i ${k8s:-arg}.list.tmp
  echo -e "\n---------\n"
done

#rm ${k8s:-arg}.list.tmp

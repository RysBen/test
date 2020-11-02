#for i in `awk '{print $1}' list2|sort|uniq`; do echo "awk '\$1==\"${i}\" {print \$2}' list2 >> list2.${i}";done

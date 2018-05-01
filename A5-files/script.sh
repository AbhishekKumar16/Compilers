cd ../150050020-150070004/
./script.sh $1

cd ../A5-files

rm *.cfg *.ast *.sym *.s
./test.sh t$1.c
# subl t$1.c.cfg t$1.c.s 
echo "cfg"
diff -wB t$1.c.cfg ../150050020-150070004/t$1.c.cfg
echo "assembly"
diff -wB t$1.c.s ../150050020-150070004/t$1.c.s
echo "ast"
diff -wB t$1.c.ast ../150050020-150070004/t$1.c.ast
# echo "symbol_table"
# diff -wB t$1.c.sym ../150050020-150070004/t$1.c.sym
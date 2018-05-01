rm *.cfg *.ast *.sym *.s
python3 Parser.py t$1.c
# subl t$1.c.cfg1 t$1.c.s 

ch_test: generator.o test.o sin_table.o
	gcc -o ch_test generator.o test.o sin_table.o

generator.o: generator.c generator.h defs.h
	gcc -c generator.c

test.o: test.c defs.h
	gcc -c test.c

sin_table.o: sin_table.c sin_table.h
	gcc -c sin_table.c

clean: 
	rm -f *.o ch_test

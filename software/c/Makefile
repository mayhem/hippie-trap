CFLAGS = -c -g 

ch_test: parse.o sin_table.o filter.o source.o generator.o
	gcc -o ch_test parse.o sin_table.o filter.o source.o generator.o

source.o: source.c source.h defs.h
	gcc $(CFLAGS) source.c

generator.o: generator.c generator.h defs.h
	gcc $(CFLAGS) generator.c

filter.o: filter.c filter.h defs.h
	gcc $(CFLAGS) filter.c

parse.o: parse.c defs.h
	gcc $(CFLAGS) parse.c

sin_table.o: sin_table.cc sin_table.h
	gcc $(CFLAGS) sin_table.cc

clean: 
	rm -f *.o ch_test

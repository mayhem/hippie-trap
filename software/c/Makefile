ch_test: parse.o sin_table.o
	g++ -o ch_test parse.o sin_table.o

parse.o: parse.cc defs.h
	g++ -c parse.cc

sin_table.o: sin_table.cc sin_table.h
	g++ -c sin_table.cc

clean: 
	rm -f *.o ch_test

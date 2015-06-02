ch_test: test.o sin_table.o
	g++ -o ch_test test.o sin_table.o

test.o: test.cc defs.h
	g++ -c test.cc

sin_table.o: sin_table.cc sin_table.h
	g++ -c sin_table.cc

clean: 
	rm -f *.o ch_test

ch_test: generator.o test.o sin_table.o
	g++ -o ch_test generator.o test.o sin_table.o

generator.o: generator.cc generator.h defs.h
	g++ -c generator.cc

test.o: test.cc defs.h
	g++ -c test.cc

sin_table.o: sin_table.cc sin_table.h
	g++ -c sin_table.cc

clean: 
	rm -f *.o ch_test

Implementing a sin function lookup table in 32bit integer math (to be run on an Ardunio):

To create the sin_table.h:

    gcc -o gen_sin_table gen_sin_table.c
    ./gen_sin_table > sin_table.h

To compile the test program:

    gcc -o sin_test sin.c

To run:

    ./sin_test | less

For the default sine wave, everything is fine until about t = 2000. Above that the errors
start mounting up and becoming unacceptable. :-(

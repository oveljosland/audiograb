all: pinread

pin_func.o: pin_func.c
	gcc -Wall -c -o pin_func.o pin_func.c

utils.o: utils.c
	gcc -Wall -c -o utils.o utils.c

main.o: main.c
	gcc -Wall -c -o main.o main.c

pinread: pin_func.o utils.o main.o
	gcc pin_func.o utils.o main.o -o pinread -lgpiod


clean:
	rm -f *.o pinread
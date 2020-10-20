libBackend.so: Tape.c backend.h
	gcc -fPIC -O3 -std=c99 -c Tape.c 
	gcc --shared -O3 -fPIC -std=c99 Tape.o -o libBackend.so
	rm *.o

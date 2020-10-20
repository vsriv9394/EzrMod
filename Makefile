./libTape.so: evaluateFunctionTape.c
	gcc -std=c99 -O3 -fPIC --shared evaluateFunctionTape.c -o ./libTape.so

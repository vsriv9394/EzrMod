#ifndef backend
#define backend

#include <math.h>
#include <stdio.h>

#define NEG  0
#define ABS  1
#define MAX  2
#define MIN  3
#define ADD  4
#define SUB  5
#define MUL  6
#define DIV  7
#define POW  8
#define EXP  9
#define LOG  10
#define SQRT 11
#define SIN  12
#define COS  13
#define TAN  14
#define SINH 15
#define COSH 16
#define TANH 17
#define IFEQ 18
#define IFNE 19
#define IFLT 20
#define IFGT 21
#define IFLE 22
#define IFGE 23

int forwProp(int size, int *op1, int *op2, double *value, int *oper, int *ifEnd, int *elseEnd);

void backProp(int depVar, int *op1, int *op2, double *value, double *deriv, int *oper);

#endif

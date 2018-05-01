int* foo(int *a, float *b){
	int *temp;
	*b = *a;
	*a = *b;
	return temp;
}
int *f(float x, int y){
	int z;
	int *t;
	return t;
}

void main(){
	int *y;
	float *x;
	int *ans;
	ans = f(*x,*y);
	*y=*ans;
}
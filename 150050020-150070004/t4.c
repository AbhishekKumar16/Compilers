int *d;

float f(int a, int b)
{
	int *c,m;
        c=&m;
	return 2.0;
}


void main(){
	
	int x ,y, *px, *py;
	float *q;
        px = &x;
        py= &y;
        *px= 2;
        *py = 3;

	*q = f(*px,*py);

}

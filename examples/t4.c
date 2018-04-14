int *p;
int* f(int a, int b)
{
	int *c,m;
        c=&m + b;
	return c;
}


void main(){
	
	int x ,y, *px, *py;
        px = &x;
        py= &y;
        *px= 2;
        *py = 3;
	p = f(*px,*py);

}

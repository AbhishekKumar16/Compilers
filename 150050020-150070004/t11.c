int *d;

int* f(int a, int b)
{
	int *c,m;
        c=&m;
	return c;
}


void main(){
	
	int x ,y, *px, *py, **ppx, **ppy;
        px = &x;
        py = &y;
        *px = 2;
        *py = 3;
        **ppx = *px;
        **ppy = *py;
	d = f(*px,*py + *py);

}

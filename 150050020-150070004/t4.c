int *d;

int f(int a, int b)
{
	int *c,m;
        c=&m;
	return *c+*c;
}


void main(){
	
	int x ,y, *px, *py;
        px = &x;
        py= &y;
        *px= 2;
        *py = 3;
        if (*px != *py)
        	*px = *px;
	*d = *py + f(*px+*py,*py)**px;

}

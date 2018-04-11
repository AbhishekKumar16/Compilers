int *d;

int* f(int a, int b)
{
	int *c,m;
        c=&m;
	return c;
}


void main(){
	
	int x ,y, *px, *py;
	float z,*pz;
        px = &x;
        py= &y;
        *px= 2;
        *py = 3;
        pz=&z;
        *pz=3.0;
	f(*px,*py);

}

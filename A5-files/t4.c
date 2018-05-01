int *d;

int f(int a, int b)
{
        int *c,m;
        c=&m;
        return *c;
}


int* g(int a, int b)
{
        int *c,m;
        c=&m;
        return c;
}


void main(){
        
        int x ,y, *px, *py;
        px = &x;
        py= &y;
        *px= 2;
        *py = 3;
        if (*px != *py)
                *px = *px;
        *d = f(*px,3+4*7);

}

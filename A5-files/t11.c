int *d;

int* f(int a, int b,int a1,int a2,int a3,int a4,int a5,int a6,int a7,int a8,int a9,int a10,int a11,int a12,int a13,int a14,int a15,int a16)
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
        d = f(*px,*py+*py,*py+*py,*py+*py,*py+*py,*py+*py,*py+*py,*py+*py,*py+*py,*py+*py,*py+*py,*py+*py,*py+*py,*py+*py,*py+*py,*py+*py,*py+*py,*py+*py);

}

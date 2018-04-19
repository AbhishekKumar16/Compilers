int *d;

void main(){
        
        int x ,y, *px, *py, **ppx, **ppy;
        float *fx, *fy;

        if (!(*fx <= *fy))
                *px = *py + *px + *px;

        while(*fx==*fy){
                *fx = *fy;
                **ppx = *px;
                px = &x;
        }

}

int *d;
float *gfx, *gfy;

void main(){
        
        int x ,y, *px, *py, **ppx, **ppy;
        float *fx, *fy, fl;

        if (!(*fx <= *fy))
                *px = *py + *px + *px;

        while(*gfx==*gfy){
                *fx = *fy;
                **ppx = *px;
                px = &x;
                gfx = &fl;
                *fx = *gfx / *gfy;
        }

}

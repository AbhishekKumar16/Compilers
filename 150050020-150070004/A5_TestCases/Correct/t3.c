int *g;

int* f(int a, int c)
{
	int *b,l;
	b=&l;
	return b;
}


void main(){
	
	int x ,*y;
	y=&x;
	*y=9;
	if(*y>8){
		g = f(3,*y);
	}
}
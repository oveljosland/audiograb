#include <stdio.h>

/* set wake alarm in seconds */
int main(int argc, char *argv[])
{
	if (argc != 2)
		return 1;

	FILE *f = fopen("/sys/class/rtc/rtc0/wakealarm", "w");
	fprintf(f, "+%s\n", argv[1]);
	fclose(f);
	return 0;
}
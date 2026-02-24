#include <stdio.h>
#include <stdlib.h>

/*
 * should probably use getopt instead of parsing manually
 */

int main(int argc, char *argv[])
{
	int c, p;
	long s;
	char *f, *opt;
	FILE *fp;

	if (argc == 1)
		return 1;
	
	p = 0;
	s = 0;
	f = NULL;
	while (--argc && (*++argv)[0] == '-') {
		opt = *argv;
		while (c = *++opt)
			switch (c) {
				case 'w':
					if (--argc <= 0) {
						fprintf(stderr, "missing arguments for -w\n");
						return 1;
					}
					s = atol(*++argv);
					break;
				case 'f':
					if (--argc <= 0) {
						fprintf(stderr, "missing arguments for -f\n");
						return 1;
					}
					f = *++argv;
					break;
				case 'p':
					p = 1;
					break;
				default:
					fprintf(stderr,"wakectl: illegal option -%c\n", c);
					return 1;
			}
	}
	if (f == NULL && argc == 1)
			f = *argv;
	if (f == NULL) {
		fprintf(stderr, "wakectl: no file specified\n");
		return 1;
	}

	if (p) {
		fp = fopen(f, "r");
		if (!fp) {
			perror("fopen");
			return 1;
		}
		static int c;
		while ((c = fgetc(fp)) != EOF)
			putchar(c);
		fclose(fp);
		return 0;
	}

	if (s >= 0) {
		fp = fopen(f, "w");
		if (!fp) {
			perror("fopen");
			return 1;
		}
		fprintf(fp, "+%ld\n", s);
		fclose(fp);
		return 0;
	}
	fprintf(stderr, "Usage: wakectl [-w seconds] [-p] [-f file]\n");
	return 1;
}
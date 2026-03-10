#include "utils.h"
#include <sys/time.h>
#include <unistd.h>

long long timeInMilliseconds(void) {
	struct timeval tv;
	gettimeofday(&tv, NULL);
	return (((long long)tv.tv_sec)*1000)+(tv.tv_usec/1000);
}
#include <errno.h>
#include <gpiod.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct gpiod_line_request* init_sdio_line(const char* chip_path,
	unsigned int* offsets,
	unsigned int num_lines, enum gpiod_line_direction dir);

struct gpiod_line_request* init_gpiod_line(const char* chip_path,
	unsigned int offset,
	enum gpiod_line_direction dir);


struct gpiod_line_request* request_input_line(const char* chip_path,
	unsigned int offset,
	const char* consumer);

int request_send_pulse(struct gpiod_line_request* request,
	unsigned int offset);

int request_SD_wait_for_quiet(struct gpiod_line_request* request,
	unsigned int* offset, int time_ms);
// SPDX-License-Identifier: GPL-2.0-or-later
// SPDX-FileCopyrightText: 2023 Kent Gibson <warthog618@gmail.com>

/* Minimal example of reading a single line. */



//for debug prints set debug 1, for no prints set debug 0
#define DEBUG 0
#define CHIP_PATH  "/dev/gpiochip0"
#define DIR1_OFFSET 27
#define DIR2_OFFSET 22
#define SD2_OFFSET 18
#define SD3_OFFSET 19
#define SD5_OFFSET 20
#define SD7_OFFSET 21
#define R_SWITCH_OFFSET 11
#define S_SWITCH_OFFSET 8
#define R_EN_VOUT_OFFSET 16
#define S_EN_VOUT_OFFSET 17
#define R_EN_SWITCH_OFFSET 12
#define S_EN_SWITCH_OFFSET 7

#include "debug.h"
#include <errno.h>
#include <gpiod.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <unistd.h>
#include "pin_func.h"


int main(void) {
	/* Example configuration - customize to suit your situation. */
	static const unsigned int line_offset = 5;
	unsigned int SD_offsets[4] = { SD2_OFFSET, SD3_OFFSET, SD5_OFFSET, SD7_OFFSET };
	unsigned int latch_offsets[6] = { R_SWITCH_OFFSET,    R_EN_VOUT_OFFSET,
									 R_EN_SWITCH_OFFSET, S_SWITCH_OFFSET,
									 S_EN_VOUT_OFFSET,   S_EN_SWITCH_OFFSET };

	struct gpiod_line_request* SD_req;
	enum gpiod_line_value SD_values[4];
	int ret;
	// line requests, initates the gpio lines/pins
	SD_req = init_sdio_line(CHIP_PATH, SD_offsets, 4, GPIOD_LINE_DIRECTION_INPUT);

	//wait for SD lines to be quiet. This is blocking code 
	ret = request_SD_wait_for_quiet(SD_req, SD_offsets, 5000, 15000);
	debug("No SD activity");

	//When there is no activity on SD lines, turn off power for SD card and disable switch


	return ret;
}

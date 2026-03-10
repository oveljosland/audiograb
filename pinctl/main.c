// SPDX-License-Identifier: GPL-2.0-or-later
// SPDX-FileCopyrightText: 2023 Kent Gibson <warthog618@gmail.com>

/* Minimal example of reading a single line. */

#include <errno.h>
#include <gpiod.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <unistd.h>

#include "config.h"
#include "pin_func.h"
#include "utils.h"

//for debug prints set debug 1, for no prints set debug 0
#define DEBUG 1
#include "debug.h"

int main(void) {
	/* Example configuration - customize to suit your situation. */
	static const unsigned int line_offset = 5;
	unsigned int SD_offsets[4] = { SD2_OFFSET, SD3_OFFSET, SD5_OFFSET, SD7_OFFSET };
	unsigned int latch_offsets[6] = { R_SWITCH_OFFSET,    R_EN_VOUT_OFFSET,
									 R_EN_SWITCH_OFFSET, S_SWITCH_OFFSET,
									 S_EN_VOUT_OFFSET,   S_EN_SWITCH_OFFSET };
	struct gpiod_line_request* request;
	struct gpiod_line_request* SD_req;
	struct gpiod_line_request* latch_req;

	enum gpiod_line_value value;
	enum gpiod_line_value SD_values[4];
	int ret = 1;


	// line requests, initates the gpio lines/pins
	SD_req = init_sdio_line(CHIP_PATH, SD_offsets, 4, GPIOD_LINE_DIRECTION_INPUT);
	latch_req = init_sdio_line(CHIP_PATH, latch_offsets, 6, GPIOD_LINE_DIRECTION_OUTPUT);


	// wake up and initiate SR latch incase this is the first time program is
	// running after PCB power on
	//Enable switch
	ret = request_send_pulse(latch_req, S_EN_SWITCH_OFFSET);
	//set switch to external device
	ret = request_send_pulse(latch_req, R_SWITCH_OFFSET);
	//Enable external power
	ret = request_send_pulse(latch_req, S_EN_VOUT_OFFSET);
	debug("set latch initial conditions");


	//wait for SD lines to be quiet. This is blocking code 
	ret = request_SD_wait_for_quiet(SD_req, SD_offsets, 2000);
	debug("No SD activity");
	
	//When there is no activity on SD lines, turn off power for SD card and disable switch
	ret = request_send_pulse(latch_req, R_EN_SWITCH_OFFSET);
	
	//delay to let sd card shut down "safely"
	sleep(1);
	
	//change switch position and enable
	ret = request_send_pulse(latch_req, S_SWITCH_OFFSET);
	ret = request_send_pulse(latch_req, S_EN_SWITCH_OFFSET);


	//now mount sd card and copy data 
	debug("mount upload and dismount");

	//turn off switch/sd card and delay
	ret = request_send_pulse(latch_req, R_EN_SWITCH_OFFSET);
	sleep(1);
	//change sd host
	ret = request_send_pulse(latch_req, R_SWITCH_OFFSET);
	//turn on switch/sd card
	ret = request_send_pulse(latch_req, S_EN_SWITCH_OFFSET);

	return ret;
}

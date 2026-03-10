#include "pin_func.h"
#include <unistd.h>
#include <sys/time.h>
#include <gpiod.h>


long long timeInMilliseconds(void) {
	struct timeval tv;
	gettimeofday(&tv, NULL);
	return (((long long)tv.tv_sec)*1000)+(tv.tv_usec/1000);
}

struct gpiod_line_request* init_sdio_line(const char* chip_path,
  unsigned int* offsets,
  unsigned int num_lines, enum gpiod_line_direction dir) {
  struct gpiod_request_config* req_cfg = NULL;
  struct gpiod_line_request* request = NULL;
  struct gpiod_line_settings* settings;
  struct gpiod_line_config* line_cfg;
  struct gpiod_chip* chip;
  unsigned int i;
  int ret;

  chip = gpiod_chip_open(chip_path);
  if (!chip) return NULL;

  settings = gpiod_line_settings_new();
  if (!settings) goto close_chip;

  gpiod_line_settings_set_direction(settings, dir);

  line_cfg = gpiod_line_config_new();
  if (!settings) goto close_chip;

  for (i = 0; i < num_lines; i++) {
    ret =
      gpiod_line_config_add_line_settings(line_cfg, &offsets[i], 1, settings);

    if (ret) goto free_line_config;
  }

  request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);

free_line_config:
  gpiod_line_config_free(line_cfg);

free_settings:
  gpiod_line_settings_free(settings);

close_chip:
  gpiod_chip_close(chip);

  return request;
};

struct gpiod_line_request* init_gpiod_line(const char* chip_path,
  unsigned int offset,
  enum gpiod_line_direction dir) {
  struct gpiod_request_config* req_cfg = NULL;
  struct gpiod_line_request* request = NULL;
  struct gpiod_line_settings* settings;
  struct gpiod_line_config* line_cfg;
  struct gpiod_chip* chip;
  int ret;

  chip = gpiod_chip_open(chip_path);
  if (!chip) return NULL;

  settings = gpiod_line_settings_new();
  if (!settings) goto close_chip;

  gpiod_line_settings_set_direction(settings, dir);

  line_cfg = gpiod_line_config_new();
  if (!settings) goto close_chip;

  ret = gpiod_line_config_add_line_settings(line_cfg, &offset, 1, settings);

  request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);

free_line_config:
  gpiod_line_config_free(line_cfg);

free_settings:
  gpiod_line_settings_free(settings);

close_chip:
  gpiod_chip_close(chip);

  return request;
};

struct gpiod_line_request* request_input_line(const char* chip_path, unsigned int offset, const char* consumer) {
  struct gpiod_request_config* req_cfg = NULL;
  struct gpiod_line_request* request = NULL;
  struct gpiod_line_settings* settings;
  struct gpiod_line_config* line_cfg;
  struct gpiod_chip* chip;
  int ret;

  chip = gpiod_chip_open(chip_path);
  if (!chip) return NULL;

  settings = gpiod_line_settings_new();
  if (!settings) goto close_chip;

  gpiod_line_settings_set_direction(settings, GPIOD_LINE_DIRECTION_INPUT);

  // make new line
  line_cfg = gpiod_line_config_new();
  if (!line_cfg) goto free_settings;

  // set the pin off the line and init it
  ret = gpiod_line_config_add_line_settings(line_cfg, &offset, 1, settings);

  if (ret) goto free_line_config;

  if (consumer) {
    req_cfg = gpiod_request_config_new();
    if (!req_cfg) goto free_line_config;

    gpiod_request_config_set_consumer(req_cfg, consumer);
  }

  request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);

  gpiod_request_config_free(req_cfg);

free_line_config:
  gpiod_line_config_free(line_cfg);

free_settings:
  gpiod_line_settings_free(settings);

close_chip:
  gpiod_chip_close(chip);

  return request;
}

int request_send_pulse(struct gpiod_line_request* request,
  unsigned int offset) {
  int status;

  status = gpiod_line_request_set_value(request, offset, 1);
  usleep(10);
  status = gpiod_line_request_set_value(request, offset, 0);

  return status;
}

int request_SD_wait_for_quiet(struct gpiod_line_request* request,
  unsigned int* offset, int time_ms) {
  enum gpiod_line_value prev_values[4];
  enum gpiod_line_value current_values[4];
  long long last_active, start_count;
  int ret;
  int timeout = 0; //returns timeout = 1 if 

  ret = gpiod_line_request_get_values(request, prev_values);

  start_count = timeInMilliseconds();

  //get new readings and compare with old. if different wait
  while (timeInMilliseconds() - last_active < time_ms) {
    int activity = 0;
    ret = gpiod_line_request_get_values(request, current_values); //read lines

    //timeout
    if(timeInMilliseconds() - start_count < 10){
      timeout = 1;
      return timeout;
    }
    
    //check for activity
    for (int i = 0; i < 4; i++) {
      if (prev_values[i] != current_values[i]) {
        activity = 1;
        printf("activity on %d \n", i);
      }
    }

    //reset timer and update last readings
    if (activity == 1) {
      for (int i = 0; i < 4; i++) {
        prev_values[i] = current_values[i];
        last_active = timeInMilliseconds();
      }
    }

  }
  return 1;
}

/*
Copyright (c) 2022-2027 VisionFive

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <limits.h>
#include <getopt.h>
#include <poll.h>
#include "Python.h"
#include "gpio-utils.h"
#include "c_gpio.h"
#include "event_gpio.h"

//int gpio_direction[49];
int gpio_direction[41];
VisonFive_info VisonFiveinfo;
const int (*GPIO2line)[41];
//const int (*GPIO2line)[49];

const char gpiochip[9] = "gpiochip0";

/*const int GPIO2line_VisionFive_v1[49] = {
// 0    1	2	 3	  4    5   6   7   8	9	10   11  12  13  14  15  16  17  18  19
   0,   1,  2,   3,   4,  -1,  6, -1,  8,   9,  10,  -1, -1, -1, -1, -1, -1, 17, -1, 19,
//20   21   22   23  24   25   26  27  28   29  30   31   32  33 34  35  36  37  38  39
  20,  21,  22,  -1, -1,  -1,  -1, -1, -1,  -1, -1,  -1,  -1, -1, -1,-1, -1, -1, -1, -1,
// 40  41  42  43  44  45  46  47  48
   -1, -1, -1, -1, 44, -1, 46, -1, -1
};

const int GPIO2line_VisionFive_v2[49] = {
// 0   1   2   3   4   5   6   7   8   9   10   11   12   13   14   15   16   17   18   19
   44, 60, 61, 63, 36, 59, 39, 46, 37, 45, 62,  56,  48,  -1,  -1,  49,  53,  50,  52,  51,
//20   21   22   23   24   25   26   27   28   29   30   31   32   33   34   35   36   37   38   39
  47,  54,  41,  -1,  -1,  -1,  -1,  -1, -1,  -1,   -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,  -1,
//40   41   42   43   44   45   46   47   48
  -1, -1,   -1,  -1,  42,  38,  55,  57,  58
};

int gpio_direction[49] = {
 -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
 -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
 -1, -1, -1, -1, -1, -1, -1, -1, -1
};*/

/*gpio pin and physical number mapping*
********************************/

const int GPIO2line_VisionFive_v1[41] = {
//  0    1    2    3    4    5    6   7     8    9   10   11   12   13   14   15   16   17   18   19   20
   -1,  -1,  -1,  -1,  -1,  -1,  -1,  46,  -1,  -1,  -1,  44,  -1,  22,  -1,  20,  21,  -1,  19,  -1,  -1,
// 21   22   23   24   25   26   27   28    29   30   31  32    33  34   35   36   37   38   39  40
   -1,  17,  -1,  -1,  -1,  -1,   9,  10,   8,   -1,  6,  -1,   -1,  -1,  3,   4,   1,   2,  -1,  0
  };

const int GPIO2line_VisionFive_v2[41] = {
//   0    1    2    3    4    5   6   7     8    9  10    11   12   13   14   15   16   17   18  19  20
    -1,  -1,  -1,  -1,  -1,  -1, -1,  55,  -1,  -1, -1,   42,  38,  43,  -1,  47,  54,  -1,  51, -1, -1,
//  21   22   23    24  25  26   27   28   29   30   31   32   33   34   35   36   37   38   39   40
	-1,  50,  -1,  -1, -1,  56,  45,  40,  37,  -1,  39,  -1,  -1,  -1,  63,  36,  60,  61,  -1,  44
	};

int gpio_direction[41] = {
	-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
	-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
	-1
};

int get_gpio_offset(int *gpio, unsigned int *gpiooffset) {
	int temp = *gpio;

	if (temp < 0 || temp > 40) {
		PyErr_SetString(PyExc_ValueError, "The gpio set is invalid on a VisionFive board");
		return 1;
	}

	if ((*GPIO2line)[temp] < 0) {
		PyErr_SetString(PyExc_ValueError, "The gpio set is invalid on a VisionFive board");
		return 1;
	}

	*gpiooffset = (*GPIO2line)[temp];

	return 0;
}

int pin_valid(int *gpio) {
	int temp = *gpio;

	if (temp <= 0 || temp > 40) {
		PyErr_SetString(PyExc_ValueError, "The gpio set is invalid on a VisionFive board");
		return 1;
	}
	return 0;
}

int gpio_set_value(int gpio, unsigned int value)
{
	struct gpio_v2_line_config config;
	struct gpio_v2_line_values values;
	struct gpio_v2_line_request ;
	int ret = 0, fd1;
	unsigned int i, num_lines = 1, gpiooffset = 0 ;
	unsigned int lines[2] = {0};

	memset(&config, 0, sizeof(config));
	get_gpio_offset(&gpio, &gpiooffset);
	ret = gpiotools_request_config(gpiochip, gpiooffset, &config); 
	if (ret < 0)
		goto exit_error;

	if (config.flags != GPIO_V2_LINE_FLAG_OUTPUT)
		goto exit_error;

	lines[0] = gpiooffset;
	ret = gpiotools_request_line(gpiochip, lines, num_lines,
				 &config, "gpio-hammer");

	if (ret < 0)
		goto exit_error;
	else
		fd1 = ret;

	values.mask = 0;
	values.bits = 0;

	for (i = 0; i < num_lines; i++)
		gpiotools_set_bit(&values.mask, i);

	for (i = 0; i < num_lines; i++) {
		if (value)
			gpiotools_set_bit(&values.bits, i);
	}

	ret = gpiotools_set_values(fd1, &values);
	if (ret < 0)
		goto exit_close_error;

	exit_close_error:
	ret = gpiotools_release_line(fd1);
	exit_error:
	return ret;
	
}

int gpio_get_value(int gpio, unsigned int *value)
{

	struct gpio_v2_line_config config;
	struct gpio_v2_line_values values;
	struct gpio_v2_line_request ;
	int ret = 0, fd1;
	unsigned int i, num_lines = 1, gpiooffset = 0;
	unsigned int lines[2] = {0};

	memset(&config, 0, sizeof(config));
	get_gpio_offset(&gpio, &gpiooffset);
	ret = gpiotools_request_config(gpiochip, gpiooffset, &config); 
	if (ret < 0)
		goto exit_error;

	if (config.flags != GPIO_V2_LINE_FLAG_INPUT)
		goto exit_error;

	lines[0] = gpiooffset;
	ret = gpiotools_request_line(gpiochip, lines, num_lines,
				 &config, "gpio-hammer");

	if (ret < 0)
		goto exit_error;
	else
		fd1 = ret;

	values.mask = 0;
	values.bits = 0;

	for (i = 0; i < num_lines; i++)
		gpiotools_set_bit(&values.mask, i);

	ret = gpiotools_get_values(fd1, &values);
	if (ret < 0)
		goto exit_close_error;

	for (i = 0; i < num_lines; i++)
		*value = gpiotools_test_bit(values.bits, i);

	exit_close_error:
	gpiotools_release_line(fd1);
	exit_error:
	return ret;

}

void output_gpio(int gpio, unsigned int value)
{
	gpio_set_value(gpio, value);
}

void input_gpio(int gpio, int *value)
{
	unsigned int get_value;

	gpio_get_value(gpio, &get_value);
	*value = (int) get_value;
}

int output_py(int gpio, int value) {
	unsigned int gpiooffset, set_value;

	if (get_gpio_offset(&gpio, &gpiooffset))
		return 0;

	if (gpio_direction[gpio] != OUTPUT)
	{
		PyErr_SetString(PyExc_RuntimeError, "The GPIO port has not been set up as OUTPUT");
		return 0;
	}

	if (value < 0)
			return 0;

	set_value = (unsigned int ) value;
	output_gpio(gpio, set_value);
	return 1;
}

int input_py(int gpio) {
	unsigned int gpiooffset = 0;
	int value = 0;

	if (get_gpio_offset(&gpio, &gpiooffset))
		return 0;

	if (gpio_direction[gpio] != INPUT)
	{
		PyErr_SetString(PyExc_RuntimeError, "The GPIO port has not been set up as INPUT");
		return 0;
	}

	input_gpio(gpio, &value);
	return value;
}

void set_flags(struct gpio_v2_line_config *pconf, int dir, int pud) {
	if (dir == INPUT) {
		pconf->flags &= ~GPIO_V2_LINE_FLAG_OUTPUT;
		pconf->flags |= GPIO_V2_LINE_FLAG_INPUT;
		
		if (pud == PUD_OFF) {
			pconf->flags &= ~GPIO_V2_LINE_FLAG_BIAS_PULL_DOWN;
			pconf->flags &= ~GPIO_V2_LINE_FLAG_BIAS_PULL_UP;

			pconf->flags |= GPIO_V2_LINE_FLAG_BIAS_DISABLED;
		}

		else if (pud == PUD_DOWN) {
			pconf->flags &= ~GPIO_V2_LINE_FLAG_BIAS_PULL_UP;
			pconf->flags &= ~GPIO_V2_LINE_FLAG_BIAS_DISABLED;

			pconf->flags |= GPIO_V2_LINE_FLAG_BIAS_PULL_DOWN;
		}

		else if (pud == PUD_UP) {
			pconf->flags &= ~GPIO_V2_LINE_FLAG_BIAS_PULL_DOWN;
			pconf->flags &= ~GPIO_V2_LINE_FLAG_BIAS_DISABLED;

			pconf->flags |= GPIO_V2_LINE_FLAG_BIAS_PULL_UP;
		}
	}	
	else if (dir == OUTPUT)	{
		pconf->flags |= GPIO_V2_LINE_FLAG_BIAS_DISABLED;
		pconf->flags &= ~GPIO_V2_LINE_FLAG_BIAS_PULL_DOWN;
		pconf->flags &= ~GPIO_V2_LINE_FLAG_BIAS_PULL_UP;
	
		pconf->flags &= ~GPIO_V2_LINE_FLAG_INPUT;
		pconf->flags |= GPIO_V2_LINE_FLAG_OUTPUT;
	}
}

int gpio_set_dir(int gpio, int direction, int pud)
{
	struct gpio_v2_line_config config;
	struct gpio_v2_line_request ;
	int ret = 0, fd1;
	unsigned int num_lines = 1, GPIOOffset = 0;
	unsigned int lines[2] = {0};

	memset(&config, 0, sizeof(config));
	get_gpio_offset(&gpio, &GPIOOffset);
	ret = gpiotools_request_config(gpiochip, GPIOOffset, &config);	
	if (ret < 0)
		goto exit_error;

	set_flags(&config, direction, pud);

	lines[0] = GPIOOffset;
	ret = gpiotools_request_line(gpiochip, lines, num_lines,
			     &config, "gpio-hammer");
	if (ret < 0)
		goto exit_error;
	else
		fd1 = ret;
	ret = gpiotools_release_line(fd1);
	exit_error:
	return ret;
}

int gpio_get_dir(int gpio)
{
	struct gpio_v2_line_config config;
	int ret = 0;
	unsigned int GPIOOffset = 0;

	memset(&config, 0, sizeof(config));
	get_gpio_offset(&gpio, &GPIOOffset);
	ret = gpiotools_request_config(gpiochip, GPIOOffset, &config);	
	if (ret < 0)
		return ret;

	if (config.flags & GPIO_V2_LINE_FLAG_OUTPUT)
		return OUTPUT;
	else if (config.flags & GPIO_V2_LINE_FLAG_INPUT)
		return INPUT;
	else
		return -1;
}

void setup_gpio(int gpio, int direction, int pud)
{
	gpio_set_dir(gpio, direction, pud);
}

int setup_one(int gpio, int direction, int initial, int pud) {
	unsigned int gpiooffset;
	//int pud = 0;

	if (get_gpio_offset(&gpio, &gpiooffset))
	  return 0;

	setup_gpio(gpio, direction, pud);
	gpio_direction[gpio] = direction;

	if (direction == OUTPUT && (initial == LOW || initial == HIGH)) {
		output_gpio(gpio, initial);
	}
	return 1;
}

void cleanup_one(int gpio, int *found)
{
	unsigned int gpiooffset;

	if (get_gpio_offset(&gpio, &gpiooffset))
		return;
	
	event_cleanup(gpio);

	if (gpio_direction[gpio] != -1) {
		setup_gpio(gpio, INPUT, PUD_UP);
		gpio_direction[gpio] = -1;
		*found = 1;
	}
}


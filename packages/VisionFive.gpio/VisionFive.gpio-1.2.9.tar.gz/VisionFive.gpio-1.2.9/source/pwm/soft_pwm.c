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


#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include "soft_pwm.h"
#include "../gpio/c_gpio.h"


pthread_t threads;

struct pwm_inst
{
	unsigned int gpio;
	float dutyratio;
	float freq;
	float ref_time;  // ret_time = freq / 1
	float time_slice; // ref_time / 100
	int running;
	struct timespec gpio_high_duration, gpio_low_duration;
	struct pwm_inst *next;
};
struct pwm_inst *pwm_link = NULL;

void get_duration_time(float timeslice, float duty_ratio, struct timespec *duration) {
	long long duration_time;

	// (dutyratio * time_slice)ms * 1000 = () us
	duration_time = (long long)((duty_ratio * timeslice) * 1000.0);
	// second = us / 1000,000 
	duration->tv_sec = (int)(duration_time / 1000000LL);
	// us = 1000,000 * sec
	duration_time -= (long long)duration->tv_sec * 1000000LL;
	// nsec = 1000 * us
	duration->tv_nsec = (long)duration_time * 1000L;
}

void calculate_times(struct pwm_inst *ptr)
{
	float high_duty = 0, low_duty = 0;

	high_duty = ptr->dutyratio;
	get_duration_time(ptr->time_slice, high_duty, &ptr->gpio_high_duration);
	low_duty = 100 - ptr->dutyratio;
	get_duration_time(ptr->time_slice, low_duty, &ptr->gpio_low_duration);
}

struct pwm_inst *add_pwm_inst(unsigned int gpio)
{
	struct pwm_inst *pwm_link_node;

	pwm_link_node = malloc(sizeof(struct pwm_inst));
	pwm_link_node->gpio = gpio;
	pwm_link_node->running = 0;
	pwm_link_node->next = NULL;
	// default frequency: 1 kHz , dutyratio 0.0
	pwm_link_node->freq = 1000.0;
	pwm_link_node->dutyratio = 0.0;
	pwm_link_node->ref_time = 1.0;    // 1 ms
	pwm_link_node->time_slice = 0.01;  // 0.01 ms
	calculate_times(pwm_link_node);
	
	return pwm_link_node;
}

struct pwm_inst *find_pwm_inst(unsigned int gpio)
{
	struct pwm_inst *ptr_link = pwm_link;

	if (ptr_link == NULL)
	{
		ptr_link = add_pwm_inst(gpio);
		pwm_link = ptr_link;
		return ptr_link;
	}

	while (ptr_link != NULL)
	{
		if (ptr_link->gpio == gpio)
			return ptr_link;
		if (ptr_link->next == NULL)
		{
			ptr_link->next = add_pwm_inst(gpio);
			return ptr_link->next;
		}
		ptr_link = ptr_link->next;
	}
	return NULL;
}

void remove_pwm_inst(unsigned int gpio)
{
	struct pwm_inst *ptr_current = pwm_link;
	struct pwm_inst *prev = NULL;
	struct pwm_inst *temp;

	while (ptr_current != NULL)
	{
		if (ptr_current->gpio == gpio)
		{
			if (prev == NULL)
				pwm_link = ptr_current->next;  //delete head node
			else
				prev->next = ptr_current->next; // delete middle node
			temp = ptr_current;
			ptr_current = ptr_current->next;  // ptr_current point to next node
			free(temp);
		} else {
			prev = ptr_current;
			ptr_current = ptr_current->next;
		}
	}
}

void full_sleep(struct timespec *req)
{
	struct timespec rem = {0};

	if (nanosleep(req,&rem) == -1)
		full_sleep(&rem);
}

void *pwm_thread(void *ptr)
{
	struct pwm_inst *pwm_node = (struct pwm_inst *)ptr;

	while (pwm_node->running)
	{
		if (pwm_node->dutyratio > 0.0)
		{
			gpio_set_value(pwm_node->gpio, 1);
			full_sleep(&pwm_node->gpio_high_duration);
		}

		if (pwm_node->dutyratio < 100.0)
		{
			gpio_set_value(pwm_node->gpio, 0);
			full_sleep(&pwm_node->gpio_low_duration);
		}
	}

	gpio_set_value(pwm_node->gpio, 0);
	remove_pwm_inst(pwm_node->gpio);
	pthread_exit(NULL);
}

void pwm_set_dutyratio(unsigned int gpio, float dutyratio)
{
	struct pwm_inst *ptr;

	if (dutyratio < 0.0 || dutyratio > 100.0)
	{
		return;
	}

	if ((ptr = find_pwm_inst(gpio)) != NULL)
	{
		ptr->dutyratio = dutyratio;
		calculate_times(ptr);
	}
}

void pwm_set_freq(unsigned int gpio, float freq)
{
	struct pwm_inst *ptr;

	if (freq <= 0.0)
	{
		return;
	}

	if ((ptr = find_pwm_inst(gpio)) != NULL)
	{
		ptr->ref_time = 1000.0 / freq;    // calculated in ms
		ptr->time_slice = ptr->ref_time / 100.0;
		calculate_times(ptr);
	}
}

void pwm_start(unsigned int gpio)
{
	struct pwm_inst *ptr;

	if (((ptr = find_pwm_inst(gpio)) == NULL) || ptr->running)
		return;

	ptr->running = 1;
	if (pthread_create(&threads, NULL, pwm_thread, (void *)ptr) != 0)
	{
		ptr->running = 0;
		return;
	}
}

void pwm_stop(unsigned int gpio)
{
	struct pwm_inst *ptr;

	if ((ptr = find_pwm_inst(gpio)) != NULL)
		ptr->running = 0;
}



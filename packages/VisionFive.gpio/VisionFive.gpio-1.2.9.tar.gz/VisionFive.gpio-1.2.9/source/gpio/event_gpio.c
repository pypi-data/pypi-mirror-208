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

#include <pthread.h>
#include <sys/epoll.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <inttypes.h>
#include <unistd.h>
#include <string.h>
#include <sys/time.h>
#include "event_gpio.h"
#include "c_gpio.h"
#include "gpio-utils.h"

const char *stredge[4] = {"none", "rising", "falling", "both"};

int event_occurred[41] = { 0 };
struct detected_event detected_event_type[41] = { 0 };
int thread_running = 0;
int epfd_thread_tbl[EPFD_THREAD_MAX] = {
// 0
  -1,
// 1   2   3   4   5   6   7   8   9   10
  -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
  -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
  -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
  -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 };

int epfd_blocking_tbl[EPFD_BLOCk_MAX] = {
// 0
  -1,
// 1   2   3   4   5   6   7   8   9   10
  -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
  -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
  -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
  -1, -1, -1, -1, -1, -1, -1, -1, -1, -1 };

struct gpios
{
	int gpio;
	int event_fd;
	int edge;
	int thread_added;
	int bouncetime;
	struct gpios *next;
};
struct gpios *gpio_list = NULL;

// event callbacks
struct callback
{
	unsigned int gpio;
	void (*func)(int gpio, int edge_type);
	struct callback *next;
};
struct callback *callbacks = NULL;

int get_event_fd(int gpio, int edge, int bntime_us)
{
	struct gpio_v2_line_config config;
	//struct gpio_v2_line_values values;
	unsigned int lines[GPIO_V2_LINES_MAX], GPIOOffset = 0;
	int attr, i, ret, num_lines = 1;

	memset(&config, 0, sizeof(config));
	config.flags |= GPIO_V2_LINE_FLAG_INPUT;

	if (edge == RISING_EDGE) 
		config.flags |= GPIO_V2_LINE_FLAG_EDGE_RISING;
	else if (edge == FALLING_EDGE)
		config.flags |= GPIO_V2_LINE_FLAG_EDGE_FALLING;
	else if (edge == BOTH_EDGE)
		config.flags |= (GPIO_V2_LINE_FLAG_EDGE_RISING | GPIO_V2_LINE_FLAG_EDGE_FALLING);

	if (bntime_us > 0) {
		attr = config.num_attrs;
		config.num_attrs++;
		for (i = 0; i < num_lines; i++)
			gpiotools_set_bit(&config.attrs[attr].mask, i);
		config.attrs[attr].attr.id = GPIO_V2_LINE_ATTR_ID_DEBOUNCE;
		config.attrs[attr].attr.debounce_period_us = bntime_us * 1000;
	}

	get_gpio_offset(&gpio, &GPIOOffset);
	lines[0] = GPIOOffset ;
	ret = gpiotools_request_line(gpiochip, lines, num_lines, &config,
					 "gpio-event-mon");

	return ret;
}


/********* gpio list functions **********/
struct gpios *get_gpio(int gpio)
{
	struct gpios *g = gpio_list;
	while (g != NULL) {
		if (g->gpio == gpio)
			return g;
		g = g->next;
	}
	return NULL;
}

struct gpios *get_gpio_from_event_fd(int fd)
{
	struct gpios *g = gpio_list;
	while (g != NULL) {
		if (g->event_fd == fd)
			return g;
		g = g->next;
	}
	return NULL;
}

struct gpios *new_gpio(int gpio , int edge, int bntime)
{
	struct gpios *new_gpio;

	new_gpio = malloc(sizeof(struct gpios));
	if (new_gpio == 0) {
		return NULL;  // out of memory
	}

	new_gpio->gpio = gpio;

	if ((new_gpio->event_fd = get_event_fd(gpio, edge, bntime)) < 0) {
		free(new_gpio);
		return NULL;
	}

	new_gpio->bouncetime = -666;
	new_gpio->thread_added = 0;

	if (gpio_list == NULL) {
		new_gpio->next = NULL;
	} else {
		new_gpio->next = gpio_list;
	}
	gpio_list = new_gpio;
	return new_gpio;
}

void delete_gpio(int gpio)
{
	struct gpios *g = gpio_list;
	struct gpios *prev = NULL;

	while (g != NULL) {
		if (g->gpio == gpio) {
			if (prev == NULL)
				gpio_list = g->next;
			else
				prev->next = g->next;
			free(g);
			close(epfd_thread_tbl[gpio]);
			epfd_thread_tbl[gpio] = -1;
			return;
		} else {
			prev = g;
			g = g->next;
		}
	}
}

int gpio_event_added(int gpio)
{
	struct gpios *g = gpio_list;
	while (g != NULL) {
		if (g->gpio == gpio)
			return g->edge;
		g = g->next;
	}
	return 0;
}

/******* callback list functions ********/
int add_edge_callback(int gpio, void (*func)(int gpio, int edge_type))
{
	struct callback *cb = callbacks;
	struct callback *new_cb;

	new_cb = malloc(sizeof(struct callback));
	if (new_cb == 0)
		return -1;  // out of memory

	new_cb->gpio = gpio;
	new_cb->func = func;
	new_cb->next = NULL;

	if (callbacks == NULL) {
		// start new list
		callbacks = new_cb;
	} else {
		// add to end of list
		while (cb->next != NULL)
			cb = cb->next;
		cb->next = new_cb;
	}
	return 0;
}

int callback_exists(unsigned int gpio)
{
	struct callback *cb = callbacks;
	while (cb != NULL) {
		if (cb->gpio == gpio)
			return 1;
		cb = cb->next;
	}
	return 0;
}

void run_callbacks(unsigned int gpio, int edge_type)
{
	struct callback *cb = callbacks;
	while (cb != NULL)
	{
		if (cb->gpio == gpio)
			cb->func(cb->gpio, edge_type);
		cb = cb->next;
	}
}

void remove_callbacks(unsigned int gpio)
{
	struct callback *cb = callbacks;
	struct callback *temp;
	struct callback *prev = NULL;

	while (cb != NULL)
	{
		if (cb->gpio == gpio)
		{
			if (prev == NULL)
				callbacks = cb->next;
			else
				prev->next = cb->next;
			temp = cb;
			cb = cb->next;
			free(temp);
		} else {
			prev = cb;
			cb = cb->next;
		}
	}
}

void *poll_thread(void *threadarg)
{
	struct epoll_event events;
	struct gpio_v2_line_event event;
	struct gpios *g;
	int n, ret, i, edge_type;
	int epfd_thread;

	thread_running = 1;
	while (thread_running) {
		for(i=0; i< EPFD_THREAD_MAX; i++) {
			epfd_thread = epfd_thread_tbl[i];
			if (epfd_thread == -1) continue;
			
			n = epoll_wait(epfd_thread_tbl[i], &events, 1, 1);
			if (n > 0) {
				lseek(events.data.fd, 0, SEEK_SET);
				ret = read(events.data.fd, &event, sizeof(event));
				if (ret == -1) {
					if (errno == -EAGAIN) {
						fprintf(stderr, "nothing available\n");
					} else {
						ret = -errno;
						fprintf(stderr, "Failed to read event (%d)\n",
							ret);
					}
					thread_running = 0;
					pthread_exit(NULL);
				}
				
				if (ret != sizeof(event)) {
					fprintf(stderr, "Reading event failed\n");
					thread_running = 0;
					pthread_exit(NULL);
				}
				/*
				fprintf(stdout, "GPIO EVENT at %" PRIu64 " on line %d (%d|%d) ",
					(uint64_t)event.timestamp_ns, event.offset, event.line_seqno,
					event.seqno);
				switch (event.id) {
				case GPIO_V2_LINE_EVENT_RISING_EDGE:
					fprintf(stdout, "rising edge");
					break;
				case GPIO_V2_LINE_EVENT_FALLING_EDGE:
					fprintf(stdout, "falling edge");
					break;
				default:
					fprintf(stdout, "unknown event");
				}

				fprintf(stdout, "\n");
				*/
				
				g = get_gpio_from_event_fd(events.data.fd);
				event_occurred[g->gpio] = 1;

				switch (event.id) {
				case GPIO_V2_LINE_EVENT_RISING_EDGE:
					printf(stdout, "rising edge \n");
					detected_event_type[g->gpio].edge_type = RISING_EDGE;
					edge_type = RISING_EDGE;
					break;
				case GPIO_V2_LINE_EVENT_FALLING_EDGE:
					printf(stdout, "falling edge \n");
					detected_event_type[g->gpio].edge_type = FALLING_EDGE;
					edge_type = FALLING_EDGE;
					break;
				default:
					//fprintf(stdout, "unknown event");
					continue;
				}

				run_callbacks(g->gpio, edge_type);

			} else if (n == -1) {
				/*  If a signal is received while we are waiting,
					epoll_wait will return with an EINTR error.
					Just try again in that case.  */
				if (errno == EINTR) {
					continue;
				}
				thread_running = 0;
				pthread_exit(NULL);
			}
		}
	}

	thread_running = 0;
	pthread_exit(NULL);
}

void remove_edge_detect(int gpio)
{
	struct epoll_event ev;
	struct gpios *g = get_gpio(gpio);

	if (g == NULL)
		return;

	memset(&ev, 0, sizeof(struct epoll_event));
	ev.events = EPOLLIN | EPOLLET | EPOLLPRI;
	ev.data.fd = g->event_fd;
	epoll_ctl(epfd_thread_tbl[gpio], EPOLL_CTL_DEL, g->event_fd, &ev);

	// delete callbacks for gpio
	remove_callbacks(gpio);

	// btc fixme - check return result??
	if (g->event_fd != -1)
		close(g->event_fd);
	
	// clear edge config and set direction to input
	gpio_set_dir(gpio, 1, 2);
	g->edge = NO_EDGE;

	// btc fixme - check return result
	//gpio_unexport(gpio);
	event_occurred[gpio] = 0;
	
	detected_event_type[gpio].rising = 0;
	detected_event_type[gpio].failing = 0;

	delete_gpio(gpio);
}

int event_detected(int gpio)
{
	if (event_occurred[gpio]) {
		event_occurred[gpio] = 0;
		return 1;
	} else {
		return 0;
	}
}

void event_cleanup(int gpio)
// gpio of -666 means clean every channel used
{
	struct gpios *g = gpio_list;
	struct gpios *next_gpio = NULL;
	int i;

	while (g != NULL) {
		next_gpio = g->next;
		if ((gpio == -666) || ((int)g->gpio == gpio))
			remove_edge_detect(g->gpio);
		g = next_gpio;
	}

	if (gpio_list == NULL) {
		for (i=0; i<EPFD_BLOCk_MAX ; i++) {
			if (epfd_blocking_tbl[i] != -1) {
				close(epfd_blocking_tbl[i]);
				epfd_blocking_tbl[i] = -1;
			}
		}

		for (i=0; i<EPFD_THREAD_MAX ; i++) {
			if (epfd_thread_tbl[i] != -1) {
				close(epfd_thread_tbl[i]);
				epfd_thread_tbl[i] = -1;
			}
		}

		thread_running = 0;
	}
}

void event_cleanup_all(void)
{
	event_cleanup(-666);
}

int add_edge_detect(int gpio, int edge, int bouncetime)
// return values:
// 0 - Success
// 1 - Edge detection already added
// 2 - Other error
{
	pthread_t threads;
	struct epoll_event ev;
	long t = 0;
	struct gpios *g;
	int i = -1, j;

	memset(&ev, 0, sizeof(struct epoll_event));
	
	i = gpio_event_added(gpio);
	if (i == 0) {    // event not already added
	    if ((g = new_gpio(gpio, edge, bouncetime)) == NULL) {
			return 2;
		}

		// sz need to be modified
		//gpio_set_edge(gpio, edge);
		g->edge = edge;
		g->bouncetime = bouncetime;
	} else if (i == (int)edge) {  // get existing event
		g = get_gpio(gpio);
		if ((bouncetime != -666 && g->bouncetime != bouncetime) ||  // different event bouncetime used
			(g->thread_added))                // event already added
			return 1;
	} else {
		return 1;
	}

	//if (epfd_thread_tbl[gpio] != -1) return 1;

	// create epfd_thread if not already open
	if ((epfd_thread_tbl[gpio] == -1) && ((epfd_thread_tbl[gpio] = epoll_create(1)) == -1))
		return 2;

	// add to epoll fd
	ev.events = EPOLLIN | EPOLLET | EPOLLPRI;
	ev.data.fd = g->event_fd;
	if (epoll_ctl(epfd_thread_tbl[gpio], EPOLL_CTL_ADD, g->event_fd, &ev) == -1) {
		remove_edge_detect(gpio);
		return 2;
	}
	g->thread_added = 1;
	// start poll thread if it is not already running
	if (!thread_running) {
	    if (pthread_create(&threads, NULL, poll_thread, (void *)t) != 0) {
			remove_edge_detect(gpio);
			return 2;
		}
	}

	return 0;
}

int blocking_wait_for_edge(int gpio, int edge, int bouncetime, int timeout)
// return values:
//		1 - Success (edge detected)
//		0 - Timeout
//		-1 - Edge detection already added
//		-2 - Other error
{
	struct epoll_event events, ev;
	struct gpios *g = NULL;
	int n, ed, ret, finished = 0;

	if (callback_exists(gpio))
		return -1;

	// add gpio if it has not been added already
	ed = gpio_event_added(gpio);
	if (ed == (int)edge) {   // get existing record
		g = get_gpio(gpio);
		if (g->bouncetime != -666 && g->bouncetime != bouncetime) {
			close(g->event_fd);
			g->event_fd = 0; 
			if ((g->event_fd = get_event_fd(gpio, edge, bouncetime)) < 0) {
				return -1;
			}		
			//gpio_set_edge(gpio, edge);
			g->edge = edge;
			g->bouncetime = bouncetime;
		}
	} else if (ed == NO_EDGE) {   // not found so add event
		if ((g = new_gpio(gpio, edge, bouncetime)) == NULL) {
			return -2;
		}
		//gpio_set_edge(gpio, edge);
		g->edge = edge;
		g->bouncetime = bouncetime;
	} else {    // ed != edge - event for a different edge
		g = get_gpio(gpio);
		close(g->event_fd);
		g->event_fd = 0; 
		if ((g->event_fd = get_event_fd(gpio, edge, bouncetime)) < 0) {
			return -1;
		}		
		//gpio_set_edge(gpio, edge);
		g->edge = edge;
		g->bouncetime = bouncetime;
	}

	// create epfd_blocking if not already open
	if ((epfd_blocking_tbl[gpio] == -1) && ((epfd_blocking_tbl[gpio] = epoll_create(1)) == -1)) {
		return -2;
	}

	// add to epoll fd
	ev.events = EPOLLIN | EPOLLET | EPOLLPRI;
	ev.data.fd = g->event_fd;
	if (epoll_ctl(epfd_blocking_tbl[gpio], EPOLL_CTL_ADD, g->event_fd, &ev) == -1) {
		return -2;
	}

	// wait for edge
	while (!finished) {
		n = epoll_wait(epfd_blocking_tbl[gpio], &events, 1, timeout);

		if (n == -1) {
			/*  If a signal is received while we are waiting,
				epoll_wait will return with an EINTR error.
				Just try again in that case.  */
			if (errno == EINTR) {
			    continue;
			}
			epoll_ctl(epfd_blocking_tbl[gpio], EPOLL_CTL_DEL, g->event_fd, &ev);
			close(epfd_blocking_tbl[gpio]);
			epfd_blocking_tbl[gpio] = -1;
			return -2;
		}
		finished = 1;
	}

	if (n > 0) {
		struct gpio_v2_line_event event;
		lseek(events.data.fd, 0, SEEK_SET);
		ret = read(events.data.fd, &event, sizeof(event));
		if (ret == -1) {
			if (errno == -EAGAIN) {
				fprintf(stderr, "nothing available\n");
			} else {
				ret = -errno;
				fprintf(stderr, "Failed to read event (%d)\n",
					ret);
			}
			epoll_ctl(epfd_blocking_tbl[gpio], EPOLL_CTL_DEL, g->event_fd, &ev);
			close(epfd_blocking_tbl[gpio]);
			epfd_blocking_tbl[gpio] = -1;
			return -2;
		}
		
		if (ret != sizeof(event)) {
			fprintf(stderr, "Reading event failed\n");
			epoll_ctl(epfd_blocking_tbl[gpio], EPOLL_CTL_DEL, g->event_fd, &ev);
			close(epfd_blocking_tbl[gpio]);
			epfd_blocking_tbl[gpio] = -1;
			return -2;
		}
		/*
		fprintf(stdout, "GPIO EVENT at %" PRIu64 " on line %d (%d|%d) ",
			(uint64_t)event.timestamp_ns, event.offset, event.line_seqno,
			event.seqno);
		
		switch (event.id) {
		case GPIO_V2_LINE_EVENT_RISING_EDGE:
			fprintf(stdout, "rising edge");
			break;
		case GPIO_V2_LINE_EVENT_FALLING_EDGE:
			fprintf(stdout, "falling edge");
			break;
		default:
			fprintf(stdout, "unknown event");
		}
		fprintf(stdout, "\n");
		*/
		
		g = get_gpio_from_event_fd(events.data.fd);
		event_occurred[g->gpio] = 1;

		switch (event.id) {
		case GPIO_V2_LINE_EVENT_RISING_EDGE:
			detected_event_type[g->gpio].rising += 1;
			break;
		case GPIO_V2_LINE_EVENT_FALLING_EDGE:
			detected_event_type[g->gpio].failing += 1;
			break;
		}
		//run_callbacks(g->gpio);
	}

	epoll_ctl(epfd_blocking_tbl[gpio], EPOLL_CTL_DEL, g->event_fd, &ev);
	close(epfd_blocking_tbl[gpio]);
	epfd_blocking_tbl[gpio] = -1;

	if (n == 0) {
		return 0; // timeout
	} else {
		return 1; // edge found
	}
}

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

#define NO_EDGE      0
#define RISING_EDGE  1
#define FALLING_EDGE 2
#define BOTH_EDGE    3
#define EPFD_THREAD_MAX 41
#define EPFD_BLOCk_MAX  41 

struct detected_event
{
	unsigned int edge_type;
	unsigned int rising;
	unsigned int failing;
};

int add_edge_detect(int gpio, int edge, int bouncetime);
void remove_edge_detect(int gpio);
int add_edge_callback(int gpio, void (*func)(int gpio, int edge_type));
int event_detected(int gpio);
int gpio_event_added(int gpio);
int event_initialise(void);
void event_cleanup(int gpio);
void event_cleanup_all(void);
int blocking_wait_for_edge(int gpio, int edge, int bouncetime, int timeout);

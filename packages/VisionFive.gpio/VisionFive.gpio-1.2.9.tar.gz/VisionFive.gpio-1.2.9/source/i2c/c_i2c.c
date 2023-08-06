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
#include <stdint.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>

#include <sys/ioctl.h>

#include <linux/i2c.h>
#include <linux/i2c-dev.h>

int i2c_open(char *dev, unsigned int addr) {
	int fd_i2c;
	int ret;

	fd_i2c = open(dev, O_RDWR);
	if (fd_i2c < 0) {
		printf("Fail to open i2c device\r\n"); 
		return fd_i2c;
	}

    ret = ioctl(fd_i2c, I2C_SLAVE, addr);
    if (ret < 0) {
		printf("I2C: Failed to connect to the device\n");
		return ret;
	}

	return fd_i2c;
}

int i2c_close(int fd_i2c) {
	return (close(fd_i2c));
}

int i2c_send(int fd_i2c, unsigned char *buf, unsigned char nbytes) {
	return (write(fd_i2c, buf, nbytes));
}

int i2c_read(int fd_i2c, unsigned char *buf, unsigned char nbytes) {
	return (read(fd_i2c, buf, nbytes));
}

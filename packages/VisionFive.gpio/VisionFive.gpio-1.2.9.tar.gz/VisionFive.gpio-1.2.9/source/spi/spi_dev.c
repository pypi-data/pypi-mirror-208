// License:MIT
/*
 * SPI testing utility (using spidev driver)
 *
 * Copyright (c) 2025  VisionFive, Inc.
 * Author: lousl
 *
 */

#include <stdint.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <getopt.h>
#include <fcntl.h>
#include <time.h>
#include <sys/ioctl.h>
#include <linux/ioctl.h>
#include <sys/stat.h>
#include <linux/types.h>
#include <linux/spi/spidev.h>
#include <stdbool.h>
#include <string.h>

#include "spi_dev.h"

#ifndef __riscv
#define SPI_TX_OCTAL            0x2000      /* transmit with 8 wires */
#define SPI_RX_OCTAL            0x4000      /* receive with 8 wires */
#endif


static int      fds    = 0;
//static uint32_t mode  = 0;
static uint32_t gspeed = 500000;
static uint16_t gdelay = 0;
static uint8_t  gbits  = 8;
static int      gmode  = 0;

int spi_getdev(char *dev)
{
	fds = open(dev, O_RDWR);
	if(fds < 0){
		printf("open spi dev failed\n");
		return -1;
	}

	return 0;
}

int spi_freedev(void)
{
	int retval = close(fds);

	if(retval < 0){
		printf("close spi dev failed\n");
		return -1;
	}

	return 0;
}

int spi_setmode(int speed, int mode, int bits)
{
	int retval = 0;

	retval = ioctl(fds, SPI_IOC_WR_MODE32, &mode);
	if(retval < 0){
		printf("set spi wr mode failed\n");
		return -1;
	}

	retval = ioctl(fds, SPI_IOC_RD_MODE32, &mode);
	if(retval < 0){
		printf("set spi rd mode failed\n");
		return -1;
	}

	retval = ioctl(fds, SPI_IOC_WR_BITS_PER_WORD, &bits);
	if(retval < 0){
		printf("set wr bits failed\n");
		return -1;
	}

	retval = ioctl(fds, SPI_IOC_RD_BITS_PER_WORD, &bits);
	if(retval < 0){
		printf("set rd bits failed\n");
		return -1;
	}

	retval = ioctl(fds, SPI_IOC_WR_MAX_SPEED_HZ, &speed);
	if(retval < 0){
		printf("set wr speed failed\n");
		return -1;
	}

	retval = ioctl(fds, SPI_IOC_RD_MAX_SPEED_HZ, &speed);
	if(retval < 0){
		printf("set wrd speed failed\n");
		return -1;
	}

	gmode = mode;
	gspeed = speed;
	gbits = bits;

	printf("Set Spi mode successfully\n");
	printf("spi mode: 0x%x\n", mode);
	printf("bits per word: %u\n", bits);
	printf("max speed: %u Hz (%u kHz)\n", speed, speed/1000);

	return 0;

}

int spi_transfer(unsigned char *data, int len)
{
	int                     retval     = 0;
	unsigned char           *recv_data = NULL;
	struct spi_ioc_transfer tr;

	memset((unsigned char *)&tr, 0, sizeof(struct spi_ioc_transfer));

	recv_data = malloc(len);
	if(recv_data == NULL){
		printf("recv data mem error\n");
		return -1;
	}
	memset(recv_data, 0, len);

	tr.tx_buf        = (unsigned long)data;
	tr.rx_buf        = (unsigned long)recv_data;
	tr.len           = len;
	tr.delay_usecs   = gdelay;
	tr.speed_hz      = gspeed;
	tr.bits_per_word = gbits;

	if(gmode & SPI_TX_OCTAL)
		tr.tx_nbits = 8;
	else if(gmode & SPI_TX_QUAD)
		tr.tx_nbits = 4;
	else if(gmode & SPI_TX_DUAL)
		tr.tx_nbits = 2;
	if(gmode & SPI_RX_OCTAL)
		tr.rx_nbits = 8;
	else if(gmode & SPI_RX_QUAD)
		tr.rx_nbits = 4;
	else if(gmode & SPI_RX_DUAL)
		tr.rx_nbits = 2;
	if(!(gmode & SPI_LOOP)){
		if(gmode & (SPI_TX_OCTAL | SPI_TX_QUAD | SPI_TX_DUAL))
			tr.rx_buf = 0;
		else if(gmode & (SPI_RX_OCTAL | SPI_RX_QUAD | SPI_RX_DUAL))
			tr.tx_buf = 0;
	}


	retval = ioctl(fds, SPI_IOC_MESSAGE(1), &tr);
	if (retval < 1){
		printf("can't send spi message");
		free(recv_data);
		return -1;
	}

	free(recv_data);
	return 0;
}

/*********************************************************
* write data to the device using system function
*********************************************************/
int spi_write(unsigned char * tx_buffer, int tx_len)
{
	return (write(fds, tx_buffer, tx_len));
}

/*********************************************************
* write data to the device using system function
*********************************************************/
int spi_read(unsigned char *rx_buffer, int rx_len)
{
	return read(fds, rx_buffer, rx_len);
}

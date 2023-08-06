#ifndef __SPI_DEV_H__
#define __SPI_DEV_H__

extern int spi_setmode(int speed, int mode, int bits);
extern int spi_transfer(unsigned char *data, int len);

//write data to slave device
extern int spi_write(unsigned char *tx_buffer, int tx_len);
//read data from slave device
extern int spi_read(unsigned char *rx_buffer, int rx_len);

extern int spi_getdev(char *dev);
extern int spi_freedev(void);

#endif

// License:MIT
/*
 * SPI testing utility (using spidev driver)
 *
 * Copyright (c) 2025  VisionFive, Inc.
 * Author: lousl
 *
 */

#include "Python.h"
#include "spi_dev.h"

#define MAX_TRANS_BYTES 4096 

static const char moduledocstring[] = "SPI functionality of a VisionFive1 using Python";

static PyObject *py_spi_getdev(PyObject *self, PyObject *args)
{
	   char          *dev     = NULL;
	   int           datalen  = 0;
	   int           retval   = 0;

	   //get Item count
	   datalen = PyTuple_Size(args);
	   if(datalen != 1){
		   PyErr_SetString(PyExc_RuntimeError, "SPI get dev input error");
		   return 0;
	   }

	   if(!PyArg_ParseTuple(args, "s", &dev)){
	   		PyErr_SetString(PyExc_RuntimeError, "dev args Parse failed");
	   		return 0;
	   	}

	   retval = spi_getdev(dev);

	   return Py_BuildValue("i", retval);
}

static PyObject *py_spi_freedev(PyObject *self, PyObject *args)
{

	   int retval = spi_freedev();
	   if(retval < 0){
		   PyErr_SetString(PyExc_RuntimeError, "free dev failed");
		   return 0;
	   }
	   return Py_BuildValue("i", retval);
}

static PyObject *py_spi_transfer(PyObject *self, PyObject *args)
{

	int			  i        = 0;
	int			  retval   = 0;
	char           *data    = NULL;
	unsigned char  datalen  = 0;
	PyObject       *p       = NULL;


	//get Item count
	datalen = PyTuple_Size(args);
	if(datalen <= 0 || datalen > 255){
	   PyErr_SetString(PyExc_RuntimeError, "SPI Transfer input error");
	   return 0;
	}
	data = malloc(sizeof(int) * datalen);
	if(data == NULL){
	   PyErr_SetString(PyExc_RuntimeError, "SPI Transfer data malloc failed");
	   return 0;
	}

	memset(data, 0, datalen);
	//Parse every data
	for(i=0; i<datalen; i++){
	   p = PyTuple_GetItem(args, i);
	   if(p == NULL){
		   PyErr_SetString(PyExc_RuntimeError, "get input data  failed");
		   return 0;
	   }
	   if(!PyArg_Parse(p, "i", &data[i])){
			 PyErr_SetString(PyExc_RuntimeError, "args Parse failed");
			 return 0;
		 }
	}

	retval = spi_transfer(data, datalen);
	if(retval < 0){
		PyErr_SetString(PyExc_RuntimeError, "SPI Transfer failed");
		return 0;
	}

	return Py_BuildValue("i", retval);
}

/*
* write bytes to slave device
* @param args Tuple with data to write
* @return none
*/
static PyObject* py_spi_write(PyObject* self, PyObject* args)
{
	PyObject *tx_list = 0;
    	PyObject *item = 0;
    
	int tx_len = 0;
        
    	/* Parse arguments */
	if(!PyArg_ParseTuple(args, "O!", &PyList_Type, &tx_list)){
		return NULL;
    	}
	/* Get length of output data */
	tx_len = PyList_Size(tx_list);
	
	/* Allocate memory for sending */
    	unsigned char * tx_buffer = (unsigned char *)malloc(tx_len * sizeof(unsigned char));
	memset(tx_buffer, 0, sizeof(unsigned char)*tx_len);

    	/* Populate both output buffer */
    	int i;
    	for(i = 0; i < tx_len; i++){
        	item = PyList_GetItem(tx_list, i);
        	tx_buffer[i] = (unsigned char)PyLong_AsLong(item);
    	}

    	/*send data */
    	unsigned char *ptr = tx_buffer;
	while(tx_len > ( MAX_TRANS_BYTES-1))
	{
		if(spi_write(ptr, MAX_TRANS_BYTES) < 0){
			return PyErr_SetFromErrno(PyExc_IOError);
		}
		ptr +=  MAX_TRANS_BYTES;
		tx_len -=  MAX_TRANS_BYTES;
	}
	if(tx_len >0){
		if(spi_write(ptr, tx_len)<0){
			return PyErr_SetFromErrno(PyExc_IOError);
		}
	}

	free(tx_buffer);
	
	Py_RETURN_NONE;
}

static PyObject* py_spi_read(PyObject *self, PyObject *args)
{
	PyObject *rx_list = NULL;
	PyObject    *item = NULL;
	int        rx_len = 0;

	/*Parse args*/
	if(!PyArg_ParseTuple(args, "i", &rx_len)){
		return NULL;
	}
	
	/*Alloctae memmory for buffer*/
	unsigned char *rx_buffer = (unsigned char*)malloc(rx_len * sizeof(unsigned char));
	memset(rx_buffer, 0, sizeof(unsigned char) * rx_len);

	/*read from slave device*/
	if(spi_read(rx_buffer, rx_len) < 0){
		Py_DECREF(rx_list);
		free(rx_buffer);
		return PyErr_SetFromErrno(PyExc_IOError);
	}

	/*Make list*/
	rx_list = PyList_New(rx_len);
	
	/*Populate list*/
	uint8_t i;
	for(i = 0; i < rx_len; i++){
		item = PyLong_FromLong(rx_buffer[i]);
		PyList_SET_ITEM(rx_list, i, item);
	}
	
	/*Do cleanp*/
	free(rx_buffer);
	
	/*Return List*/
	return rx_list;
}

static PyObject *py_spi_setmode(PyObject *self, PyObject *args)
{
	int mode   = 0;
	int speed  = 0;
	int bits   = 0;
	int retval = 0;

	if(!PyArg_ParseTuple(args, "iii", &speed, &mode, &bits)){
		PyErr_SetString(PyExc_RuntimeError, "args Parse failed");
		return 0;
	}

    retval = spi_setmode(speed, mode, bits);
    if(retval < 0){
    	PyErr_SetString(PyExc_RuntimeError, "setmode failed");
		return 0;
    }

    return Py_BuildValue("i", retval);
}


PyMethodDef vfpi_spi_methods[] = {
   {"setmode",      py_spi_setmode,                METH_VARARGS,
					"***************************************************************\n" \
					"function: set spi mode, including work mode, BITS_PER_WORD, MAX_SPEED." \
					"usage: \n" \
					"  import VisionFive.spi as SPI \n"\
					"  ##how to read and write data about ADXL345\n"\
					"  \n"\
					"  SPI.getdev('/dev/spidev1.0') \n"\
					"  SPI.setmode(500000, 3, 8) \n"\
					"  \n"\
					"  #set 0xaa to reg 0x1e \n"\
					"  SPI.write([0x1e,0xaa]) \n"\
					"  \n"\
					"  #read value of reg 0x1e \n"\
					"  SPI.write([0x9e, 0x00]) \n"\
					"  SPI.read(1) \n"\
					"  \n"\
					"  #set 0xab to reg 0x1e \n"\
					"  SPI.transfer(0x1e, 0xab) \n"\
					"  #read value of reg 0x1e \n"\
					"  SPI.transfer(0x9e, 0x00) \n"\
					"  SPI.read(1) \n"\
					"  SPI.freedev() \n"\
					"***************************************************************\n"},

   {"transfer",     (PyCFunction)py_spi_transfer,  METH_VARARGS,
					"***************************************************************\n" \
					"function: write data to spi device, or read data from spi device. \n" \
					"usage: \n" \
					"	please see usage of API open() \n"\
					"	cmd 'help(SPI.setmode) to get the detail usage' \n"\
					"***************************************************************\n"},

   {"freedev",      py_spi_freedev,                METH_VARARGS,
					"***************************************************************\n" \
					"function: close spi device. \n" \
					"usage: \n" \
					"  please see usage of API open() \n"\
					"  cmd 'help(SPI.setmode) to get the detail usage' \n"\
					"***************************************************************\n"},

   {"getdev",       py_spi_getdev,                 METH_VARARGS,
					"***************************************************************\n" \
					"function: open spi dev. \n" \
					"usage: \n" \
					"  please see usage of API open() \n"\
					"  cmd 'help(SPI.setmode) to get the detail usage' \n"\
					"***************************************************************\n"},

   {"write",        py_spi_write,                  METH_VARARGS,
					"***************************************************************\n" \
					"function: write data to slave spi device. \n" \
					"usage: \n" \
					"  please see usage of API open() \n"\
					"  cmd 'help(SPI.setmode) to get the detail usage' \n"\
					"***************************************************************\n"},

   {"read",         py_spi_read,                   METH_VARARGS,
					"***************************************************************\n" \
					"function: read data from slave spi device. \n" \
					"usage: \n" \
					"  please see usage of API open() \n"\
					"  cmd 'help(SPI.setmode) to get the detail usage' \n"\
					"***************************************************************\n"},

   {NULL,           NULL,                          METH_NOARGS,   NULL}
};

#if PY_MAJOR_VERSION > 2
static struct PyModuleDef vfispimodule = {
   PyModuleDef_HEAD_INIT,
   "VisionFive._spi",      // name of module
   moduledocstring,  // module documentation, may be NULL
   -1,               // size of per-interpreter state of the module, or -1 if the module keeps state in global variables.
   vfpi_spi_methods
};
#endif

#if PY_MAJOR_VERSION > 2
PyMODINIT_FUNC PyInit__spi(void)
#else
PyMODINIT_FUNC init_spi(void)
#endif
{
	PyObject *module;

#if PY_MAJOR_VERSION > 2
	module = PyModule_Create(&vfispimodule);
	if(module == NULL){
	   return NULL;
	}
#else
	module = Py_InitModule3("VisionFive._spi", vfpi_spi_methods, moduledocstring);
	if (module == NULL){
	   return NULL;
	}
#endif


#if PY_MAJOR_VERSION > 2
	return module;
#else
	return;
#endif
}

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


#include "Python.h"
#include "c_i2c.h"

int fd_i2c;

static PyObject* py_open(PyObject* self, PyObject *args) {
	char *i2c_dev = NULL;
	int i2c_addr = -1;

	if(!PyArg_ParseTuple(args, "si", &i2c_dev, &i2c_addr)){
			PyErr_SetString(PyExc_RuntimeError, "dev args Parse failed");
			return NULL;
	}	
		
	if (i2c_addr < 0) {
		PyErr_SetString(PyExc_ValueError, "An invalid i2c_dev was passed to open()");
		return NULL;
	}

	if(i2c_dev == NULL) {
		printf("i2c_dev is null \n");
		return NULL;
	}

	printf("i2c_dev: %s \n", i2c_dev);
	fd_i2c = i2c_open(i2c_dev, i2c_addr);
	if (fd_i2c < 0) {
		printf("Fail to open i2c device\r\n");
	}

	return Py_BuildValue("i", fd_i2c);
}

static PyObject* py_read(PyObject* self, PyObject* args) {
	int bytes = 0;
	int i = 0;
	unsigned char *buf = NULL;
	PyObject *pylist = NULL;
	PyObject *item = NULL;

	if (!PyArg_ParseTuple(args, "i", &bytes)) {
		return NULL;
	}

	if (bytes <= 0) {
		PyErr_SetString(PyExc_ValueError, "i2c read: invalid number of bytes to read");
		return NULL;
	}

	buf = (unsigned char *) malloc(bytes * sizeof (unsigned char));
	memset(buf, 0, bytes * sizeof (unsigned char));

	if (i2c_read(fd_i2c, buf, bytes) < 0) {
		Py_DECREF(pylist);
		free(buf);
		return PyErr_SetFromErrno(PyExc_IOError);
	}

	pylist = PyList_New(bytes);

	if (pylist != NULL) {
		for (i = 0; i < bytes; i++) {
			item = PyLong_FromLong(buf[i]);
			PyList_SET_ITEM(pylist, i, item);
		}
	}

	free(buf);

	return pylist;
}

static PyObject* py_write(PyObject* self, PyObject* args) {
	unsigned char *buf = NULL;
	unsigned int num = 0;
	unsigned int i = 0;
	PyObject *list = NULL;
	PyObject *item = NULL;

	if (!PyArg_ParseTuple(args, "O", &list)) {
		PyErr_SetString(PyExc_ValueError, "Invalid data type !");
		return NULL;
	}

	if(!PyList_Check(list)) {
		PyErr_SetString(PyExc_ValueError, "Only python list type should be input !");
		return NULL;
	}

	num = PyList_Size(list);
	buf = (unsigned char *)malloc(num  * sizeof(unsigned char));
	memset(buf, 0, num * sizeof (unsigned char));

	for (i = 0; i < num; i++) {
		item = PyList_GetItem(list, i);
		buf[i] = (unsigned char) PyLong_AsLong(item);
	}

	if (i2c_send(fd_i2c, buf, num) < 0) {
		return PyErr_SetFromErrno(PyExc_IOError);
	}

	free(buf);
	Py_DECREF(list);

	Py_RETURN_NONE;
}

static PyObject* py_close(PyObject* self, PyObject *args) {

	if (i2c_close(fd_i2c) < 0) {
		return PyErr_SetFromErrno(PyExc_IOError);
	}
	Py_RETURN_NONE;
}

static PyMethodDef module_methods[] = {
	{"open", py_open, METH_VARARGS,
					"***************************************************************\n" \
					"function: open I2C fd" \
					"usage: \n" \
					"  import VisionFive.i2c as I2C \n"\
					"  import time \n"\
					"  #SHTC3 is temperature and humidity sensor\n" \
					"  \n" \
					"  I2C_DEVICE = '/dev/i2c-1' \n" \
					"  SHTC3_I2C_ADDRESS = 0x70 \n" \
					"  ret = I2C.open(I2C_DEVICE, SHTC3_I2C_ADDRESS) \n" \
					"  \n" \
					"  def SHTC3_WriteCommand(cmd): \n" \
					"      buf0 =  (cmd >> 8)& 0xff \n" \
					"      buf1 = cmd & 0xff \n" \
					"      buf = [buf0, buf1] \n" \
					"      I2C.write(buf) \n" \
					"  \n" \
					"  SHTC3_WriteCommand(0x401A)\n" \
					"  time.sleep(0.03) \n" \
					"  SHTC3_WriteCommand(0x7866)\n" \
					"  time.sleep(0.02) \n" \
					"  buf_list = I2C.read(3) \n" \
					"  I2C.close()\n" \
					"***************************************************************\n"},

	{"close", py_close, METH_NOARGS,
					"***************************************************************\n" \
					"function: close I2C fd" \
					"usage: \n" \
					"  please see usage of API open() \n"\
					"  cmd 'help(I2C.open) to get the detail usage' \n"\
					"***************************************************************\n"},

	{"write", py_write, METH_VARARGS,
					"***************************************************************\n" \
					"function: write n bytes to I2C device" \
					"usage: \n" \
					"  please see usage of API open() \n"\
					"  cmd 'help(I2C.open) to get the detail usage' \n"\
					"***************************************************************\n"},
					
	{"read", py_read, METH_VARARGS,
					"***************************************************************\n" \
					"function: read n bytes from I2C device" \
					"usage: \n" \
					"  please see usage of API open() \n"\
					"  cmd 'help(I2C.open) to get the detail usage' \n"\
					"***************************************************************\n"},

	{NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef module_def = {
	PyModuleDef_HEAD_INIT,
	"VisionFive._i2c",
	NULL,
	-1,
	module_methods
};
#endif

PyMODINIT_FUNC
#if PY_MAJOR_VERSION >= 3
	PyInit__i2c(void) {
#else
	init_i2c(void) {
#endif

	PyObject* module = NULL;

#if PY_MAJOR_VERSION >= 3
	module = PyModule_Create(&module_def);
#else
	module = Py_InitModule("VisionFive._i2c", module_methods);
#endif

	if (module == NULL)
#if PY_MAJOR_VERSION >= 3
		return NULL;
#else
		return;
#endif

#if PY_MAJOR_VERSION >= 3
	return module;
#else
	return;
#endif

}




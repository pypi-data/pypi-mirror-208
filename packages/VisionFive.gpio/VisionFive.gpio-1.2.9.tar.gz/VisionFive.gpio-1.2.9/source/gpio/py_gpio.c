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
#include "c_gpio.h"
#include "event_gpio.h"
#include "py_constants.h"
#include "cpuinfo.h"
#include "../pwm/py_pwm.h"

static int gpio_warnings = 1;
int gpio_mode = MODE_UNKNOWN;
extern struct detected_event detected_event_type[41];

struct py_callback
{
   int gpio;
   PyObject *py_cb;
   struct py_callback *next;
};
static struct py_callback *py_callbacks = NULL;


int pin_check(PyObject *tempobj, int *gpioport) {
	unsigned int gpiooffset;

#if PY_MAJOR_VERSION > 2
		if (PyLong_Check(tempobj)) {
			*gpioport = (int)PyLong_AsLong(tempobj);
#else
		if (PyInt_Check(tempobj)) {
			*gpioport = (int)PyInt_AsLong(tempobj);
#endif
		if (PyErr_Occurred())
			return 1;
		} else {
			PyErr_SetString(PyExc_ValueError, "gpioport must be an integer");
			return 1;
		}
		if (pin_valid(gpioport))
			return 1;

		return 0;
}


int int_check(PyObject *tempobj, int *gpioport) {
	unsigned int gpiooffset;

#if PY_MAJOR_VERSION > 2
		if (PyLong_Check(tempobj)) {
			*gpioport = (int)PyLong_AsLong(tempobj);
#else
		if (PyInt_Check(tempobj)) {
			*gpioport = (int)PyInt_AsLong(tempobj);
#endif
		if (PyErr_Occurred())
			return 1;
		} else {
			PyErr_SetString(PyExc_ValueError, "gpioport must be an integer");
			return 1;
		}
		if (get_gpio_offset(gpioport, &gpiooffset))
			return 1;

		return 0;
}

int GPIO_Data_check(PyObject *gpiolist, PyObject *gpiotuple, int *gpioport, int *gpiocount) {

#if PY_MAJOR_VERSION > 2
		if (PyLong_Check(gpiolist)) {
			*gpioport = (int)PyLong_AsLong(gpiolist);
#else
		if (PyInt_Check(gpiolist)) {
			*gpioport = (int)PyInt_AsLong(gpiolist);
#endif
			if (PyErr_Occurred())
				return 1;
			gpiolist = NULL;
		} else if (PyList_Check(gpiolist)) {
			*gpiocount = PyList_Size(gpiolist);
		} else if (PyTuple_Check(gpiolist)) {
			gpiotuple = gpiolist;
			gpiolist = NULL;
			*gpiocount = PyTuple_Size(gpiotuple);
		} else {
			// raise exception
			PyErr_SetString(PyExc_ValueError, "gpioport must be an integer or list/tuple of integers");
			return 1;
		}
		return 0;
}

/*
* python function cleanup(gpioport=None)
**clean up GPIO0, tow different input format are allowed
*  	GPIO.cleanup(gp=0)
*  	GPIO.cleanup(0)
*
** clear up all GPIO ports
*   GPIO.cleanup()
*/
static PyObject *py_cleanup(PyObject *self, PyObject *args, PyObject *kwargs)
{
	int ret, i;
	int gpiocount = -255;
	int found = 0;
	int gpioport = -255;
	unsigned int gpiooffset;
	PyObject *gpiolist = NULL;
	PyObject *gpiotuple = NULL;
	PyObject *tempobj;
	static char *kwlist[] = {"channel", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|O", kwlist, &gpiolist))
		return NULL;

	if (gpiolist == NULL) {  // gpioport kwarg not set
	// do nothing
	}
	else {
		ret = GPIO_Data_check(gpiolist, gpiotuple, &gpioport, &gpiocount);
		if (ret == 1)
			return NULL;
	}

	if (gpioport == -255 && gpiocount == -255) {
		for (i = 0; i < 41; i++) {
			if (gpio_direction[i] != -1) {
				setup_gpio(i, INPUT, PUD_UP);
				gpio_direction[i] = -1;
				found = 1;
			}
		}
	} else if (gpioport != -255) {

	if (get_gpio_offset(&gpioport, &gpiooffset))
		return NULL;
	cleanup_one(gpioport, &found);

	} else {  
		// gpioport was a list/tuple

		for (i = 0; i < gpiocount; i++) {
			if (gpiolist) {
				if ((tempobj = PyList_GetItem(gpiolist, i)) == NULL) {
					return NULL;
				}
			} else { // assume gpiotuple
				if ((tempobj = PyTuple_GetItem(gpiotuple, i)) == NULL) {
					return NULL;
				}
			}

			ret = int_check(tempobj, &gpioport);
			if (ret == 1)
				return NULL;
			cleanup_one(gpioport, &found);
		}
	}


	// check if any gpioports set up - if not warn about misuse of GPIO.cleanup()
	if (!found ) {
		PyErr_WarnEx(NULL, "None of gpioports has been set up !", 1);
	}

	Py_RETURN_NONE;
}

/*
*
**different input format are allowed
*  	GPIO.setup(channel=0, direction=GPIO.OUT)
*  	GPIO.setup(0, GPIO.OUT)
**Also serveral GPIO ports can be set at one time
*   GPIO.setup(channel=[0, 2, 4], direction=GPIO.OUT)
*   GPIO.setup([0, 2, 4], GPIO.OUT)
*/
static PyObject *py_setup_gpioport(PyObject *self, PyObject *args, PyObject *kwargs)
{
	int gpioport = -255;
	int direction = -1;
	int initial = -1;
	int i = 0, ret = 0;
	int gpiocount = -255;
	int pud = PUD_OFF;
	int pud_in = -1;
	unsigned int gpiooffset;
	static char *kwlist[] = {"channel", "direction", "pull_up_down", "initial", NULL};
	PyObject *gpiolist = NULL;
	PyObject *gpiotuple = NULL;
	PyObject *tempobj;

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Oi|ii", kwlist, &gpiolist, &direction, &pud_in, &initial))
		return NULL;

	ret = GPIO_Data_check(gpiolist, gpiotuple, &gpioport, &gpiocount);
	if (ret == 1)
		return NULL;

	if (direction != INPUT && direction != OUTPUT) {
		PyErr_SetString(PyExc_ValueError, "An invalid direction was passed to setup()");
		return 0;
	}

	if (pud_in != -1)  pud = pud_in;
	
	if (direction == OUTPUT && pud != PUD_OFF) {
		PyErr_SetString(PyExc_ValueError, "pull_up_down parameter is not valid for outputs");
		return 0;
	}

	if (direction == INPUT && initial != -1) {
		PyErr_SetString(PyExc_ValueError, "initial parameter is not valid for inputs");
		return 0;
	}

	if (pud != PUD_OFF && pud != PUD_DOWN && pud != PUD_UP) {
		PyErr_SetString(PyExc_ValueError, "Invalid value for pull_up_down - should be either PUD_OFF, PUD_UP or PUD_DOWN");
		return NULL;
	}

	if ( pud_in == -1 && pud == PUD_OFF && direction == INPUT) pud = PUD_UP;

	if (gpioport != -255) {    // the type of gp is a single gpioport

	 if (get_gpio_offset(&gpioport, &gpiooffset))
		return NULL;

	 if (!setup_one(gpioport, direction, initial, pud))
		return NULL;

	 Py_RETURN_NONE;
	}

	for (i = 0; i< gpiocount; i++) {
		if (gpiolist) {
			if ((tempobj = PyList_GetItem(gpiolist, i)) == NULL) {
				return NULL;
			}
		} else { // assume gpiotuple
			if ((tempobj = PyTuple_GetItem(gpiotuple, i)) == NULL) {
				return NULL;
			}
		}

		ret = int_check(tempobj, &gpioport);
		if (ret == 1)
			return NULL;

		if (!setup_one(gpioport, direction, initial, pud))
			return NULL;
	}

   Py_RETURN_NONE;
}

// python function output_py(gpioport(s), value(s))
static PyObject *py_output_gpio(PyObject *self, PyObject *args)
{
	int gpioport = -1;
	int value = -1;
	int gpiocount = -1;
	int valuecount = -1;
	int i = 0;
	PyObject *gpiolist = NULL;
	PyObject *valuelist = NULL;
	PyObject *gpiotuple = NULL;
	PyObject *valuetuple = NULL;
	PyObject *tempobj = NULL;

	if (!PyArg_ParseTuple(args, "OO", &gpiolist, &valuelist))
		return NULL;

#if PY_MAJOR_VERSION >= 3
	if (PyLong_Check(gpiolist)) {
		gpioport = (int)PyLong_AsLong(gpiolist);
#else
	if (PyInt_Check(gpiolist)) {
		gpioport = (int)PyInt_AsLong(gpiolist);
#endif
		if (PyErr_Occurred())
			return NULL;
		gpiolist = NULL;
	} else if (PyList_Check(gpiolist)) {
	// do nothing
	} else if (PyTuple_Check(gpiolist)) {
		gpiotuple = gpiolist;
		gpiolist = NULL;
	} else {
		PyErr_SetString(PyExc_ValueError, "gpioport must be an integer or list/tuple of integers");
		return NULL;
	}

#if PY_MAJOR_VERSION >= 3
	if (PyLong_Check(valuelist)) {
		value = (int)PyLong_AsLong(valuelist);
#else
	if (PyInt_Check(valuelist)) {
		value = (int)PyInt_AsLong(valuelist);
#endif
		if (PyErr_Occurred())
			return NULL;
		valuelist = NULL;
	} else if (PyList_Check(valuelist)) {
	// do nothing
	} else if (PyTuple_Check(valuelist)) {
		valuetuple = valuelist;
		valuelist = NULL;
	} else {
		PyErr_SetString(PyExc_ValueError, "Value must be an integer/boolean or a list/tuple of integers/booleans");
		return NULL;
	}

	if (gpiolist)
		gpiocount = PyList_Size(gpiolist);
	if (gpiotuple)
		gpiocount = PyTuple_Size(gpiotuple);
	if (valuelist)
		valuecount = PyList_Size(valuelist);
	if (valuetuple)
		valuecount = PyTuple_Size(valuetuple);
	if ((gpiocount != -1 && gpiocount != valuecount && valuecount != -1) || (gpiocount == -1 && valuecount != -1)) {
		PyErr_SetString(PyExc_RuntimeError, "Number of gpioports != number of values");
		return NULL;
	}

	if (gpiocount == -1) {
		if (!output_py(gpioport, value))
			return NULL;
		Py_RETURN_NONE;
   }

	for (i=0; i<gpiocount; i++) {
		// get gpioport number
		if (gpiolist) {
			if ((tempobj = PyList_GetItem(gpiolist, i)) == NULL) {
				return NULL;
		 }
		} else { // assume gpiotuple
			if ((tempobj = PyTuple_GetItem(gpiotuple, i)) == NULL) {
				return NULL;
			}
		}

#if PY_MAJOR_VERSION >= 3
	if (PyLong_Check(tempobj)) {
		gpioport = (int)PyLong_AsLong(tempobj);
#else
	if (PyInt_Check(tempobj)) {
		gpioport = (int)PyInt_AsLong(tempobj);
#endif
	if (PyErr_Occurred())
		return NULL;
	} else {
		PyErr_SetString(PyExc_ValueError, "gpioport must be an integer");
		return NULL;
	}

	// get value
	if (valuecount > 0) {
			if (valuelist) {
				if ((tempobj = PyList_GetItem(valuelist, i)) == NULL) {
					return NULL;
			}
			} else { // assume valuetuple
				if ((tempobj = PyTuple_GetItem(valuetuple, i)) == NULL) {
					return NULL;
				}
			}
#if PY_MAJOR_VERSION >= 3
			if (PyLong_Check(tempobj)) {
				value = (int)PyLong_AsLong(tempobj);
#else
			if (PyInt_Check(tempobj)) {
				value = (int)PyInt_AsLong(tempobj);
#endif
				if (PyErr_Occurred())
					return NULL;
			} else {
				PyErr_SetString(PyExc_ValueError, "Value must be an integer or boolean");
				return NULL;
			}
		}
		if (!output_py(gpioport, value))
			return NULL;
	}

	Py_RETURN_NONE;
}

// python function setmode(mode)
static PyObject *py_setmode(PyObject *self, PyObject *args) {
	 Py_RETURN_NONE;
}

// python function getmode()
static PyObject *py_getmode(PyObject *self, PyObject *args) {
	PyObject *value;

	value = Py_BuildValue("i", gpio_mode);
	return value;
}

// python function value = input_py(gpioport)
static PyObject *py_input_gpio(PyObject *self, PyObject *args)
{
	int gpioport = -1;
	unsigned int gpiooffset = 0;
	PyObject *value;

	if (!PyArg_ParseTuple(args, "i", &gpioport))
		return NULL;

	if (get_gpio_offset(&gpioport, &gpiooffset))
		return NULL;

	// check gpioport is set up as an input or output
	if (gpio_direction[gpioport] != INPUT && gpio_direction[gpioport] != OUTPUT)
	{
		PyErr_SetString(PyExc_RuntimeError, "You must setup() the GPIO gpioport first");
		return NULL;
	}

	if (input_py(gpioport)) {
		value = Py_BuildValue("i", HIGH);
	} else {
		value = Py_BuildValue("i", LOW);
	}
	return value;
}

static void run_py_callbacks(int gpio, int edge_type)
{
	PyObject *result;
	PyGILState_STATE gstate;
	struct py_callback *cb = py_callbacks;

	while (cb != NULL)
	{
		if (cb->gpio == gpio) {
			// run callback
			gstate = PyGILState_Ensure();
			result = PyObject_CallFunction(cb->py_cb, "ii", gpio, edge_type);
			if (result == NULL && PyErr_Occurred()){
			PyErr_Print();
			PyErr_Clear();
			}
			Py_XDECREF(result);
			PyGILState_Release(gstate);
		}
		cb = cb->next;
   }
}

static int add_py_callback(int gpio, PyObject *cb_func)
{
	struct py_callback *new_py_cb;
	struct py_callback *cb = py_callbacks;

	// add callback to py_callbacks list
	new_py_cb = malloc(sizeof(struct py_callback));
	if (new_py_cb == 0)
	{
		PyErr_NoMemory();
		return -1;
	}
	new_py_cb->py_cb = cb_func;
	Py_XINCREF(cb_func);         // Add a reference to new callback
	new_py_cb->gpio = gpio;
	new_py_cb->next = NULL;
	if (py_callbacks == NULL) {
		py_callbacks = new_py_cb;
	} else {
	// add to end of list
	while (cb->next != NULL)
		cb = cb->next;
	cb->next = new_py_cb;
	}
	add_edge_callback(gpio, run_py_callbacks);
	return 0;
}

// python function add_event_callback(gpio, callback)
static PyObject *py_add_event_callback(PyObject *self, PyObject *args, PyObject *kwargs)
{
	unsigned int gpiooffset;
	int gpio;
	PyObject *cb_func;
	char *kwlist[] = {"gpio", "callback", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "iO|i", kwlist, &gpio, &cb_func))
		return NULL;

	if (!PyCallable_Check(cb_func))
	{
		PyErr_SetString(PyExc_TypeError, "Parameter must be callable");
		return NULL;
	}

	if (get_gpio_offset(&gpio, &gpiooffset))
		return NULL;

	// check channel is set up as an input
	if (gpio_direction[gpio] != INPUT)
	{
		PyErr_SetString(PyExc_RuntimeError, "You must setup() the GPIO pin as an input first");
		return NULL;
	}

	if (!gpio_event_added(gpio))
	{
		PyErr_SetString(PyExc_RuntimeError, "Add event detection using add_event_detect first before adding a callback");
		return NULL;
	}

	if (add_py_callback(gpio, cb_func) != 0)
		return NULL;

	Py_RETURN_NONE;
}

// python function add_event_detect(gpio, edge, callback=None, bouncetime=None)
static PyObject *py_add_event_detect(PyObject *self, PyObject *args, PyObject *kwargs)
{
	unsigned int gpiooffset;
	int gpio, edge, result;
	int bouncetime = -666;
	PyObject *cb_func = NULL;
	char *kwlist[] = {"gpio", "edge", "callback", "bouncetime", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ii|Oi", kwlist, &gpio, &edge, &cb_func, &bouncetime))
		return NULL;

	if (cb_func != NULL && !PyCallable_Check(cb_func))
	{
		PyErr_SetString(PyExc_TypeError, "Parameter must be callable");
		return NULL;
	}

	if (get_gpio_offset(&gpio, &gpiooffset))
		return NULL;

	// check channel is set up as an input
	if (gpio_direction[gpio] != INPUT)
	{
		PyErr_SetString(PyExc_RuntimeError, "You must setup() the GPIO pin as an input first");
		return NULL;
	}

	// is edge valid value
	//edge -= PY_EVENT_CONST_OFFSET;
	if (edge != RISING_EDGE && edge != FALLING_EDGE && edge != BOTH_EDGE)
	{
		PyErr_SetString(PyExc_ValueError, "The edge must be set to RISING, FALLING or BOTH");
		return NULL;
	}

	if (bouncetime <= 0 && bouncetime != -666)
	{
		PyErr_SetString(PyExc_ValueError, "Bouncetime must be greater than 0");
		return NULL;
	}

	if ((result = add_edge_detect(gpio, edge, bouncetime)) != 0)   // starts a thread
	{
		if (result == 1)
		{
			PyErr_SetString(PyExc_RuntimeError, "Conflicting edge detection already enabled for this GPIO pin");
			return NULL;
		} else {
			PyErr_SetString(PyExc_RuntimeError, "Failed to add edge detection");
			return NULL;
		}
	}

	if (cb_func != NULL)
		if (add_py_callback(gpio, cb_func) != 0)
			return NULL;

	Py_RETURN_NONE;
}

// python function remove_event_detect(gpio)
static PyObject *py_remove_event_detect(PyObject *self, PyObject *args)
{
	unsigned int gpiooffset;
	int gpio;
	struct py_callback *cb = py_callbacks;
	struct py_callback *temp;
	struct py_callback *prev = NULL;

	if (!PyArg_ParseTuple(args, "i", &gpio))
		return NULL;

	if (get_gpio_offset(&gpio, &gpiooffset))
		return NULL;

	// remove all python callbacks for gpio
	while (cb != NULL)
	{
		if (cb->gpio == gpio)
		{
			Py_XDECREF(cb->py_cb);
			if (prev == NULL)
				py_callbacks = cb->next;
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

	remove_edge_detect(gpio);

	Py_RETURN_NONE;
}

// python function value = event_detected(channel)
static PyObject *py_event_detected(PyObject *self, PyObject *args)
{
	unsigned int gpiooffset;
	int gpio;

	if (!PyArg_ParseTuple(args, "i", &gpio))
		return NULL;

	if (get_gpio_offset(&gpio, &gpiooffset))
		return NULL;

	if (event_detected(gpio))
		Py_RETURN_TRUE;
	else
		Py_RETURN_FALSE;
}

// python function value = py_get_detected_event(gpio)
static PyObject *py_get_detected_event(PyObject *self, PyObject *args)
{
	unsigned int gpiooffset;
	int gpio;

	if (!PyArg_ParseTuple(args, "i", &gpio))
		return NULL;

	if (get_gpio_offset(&gpio, &gpiooffset))
		return NULL;

	if (detected_event_type[gpio].edge_type == RISING_EDGE) {
		detected_event_type[gpio].edge_type = NO_EDGE;
		return Py_BuildValue("i", 1);
	}
	else if (detected_event_type[gpio].edge_type == FALLING_EDGE) {
		detected_event_type[gpio].edge_type = NO_EDGE;
		return Py_BuildValue("i", 2);
	}
	else
		return Py_BuildValue("i", 0);
}

// python function channel = wait_for_edge(gpio, edge, bouncetime=None, timeout=None)
static PyObject *py_wait_for_edge(PyObject *self, PyObject *args, PyObject *kwargs)
{
	unsigned int gpiooffset;
	int gpio, edge, result;
	int bouncetime = -666; // None
	int timeout = -1; // None

	static char *kwlist[] = {"channel", "edge", "bouncetime", "timeout", NULL};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ii|ii", kwlist, &gpio, &edge, &bouncetime, &timeout))
		return NULL;

	if (get_gpio_offset(&gpio, &gpiooffset))
		return NULL;

	// check channel is setup as an input
	if (gpio_direction[gpio] != INPUT)
	{
		PyErr_SetString(PyExc_RuntimeError, "You must setup() the GPIO pin as an input first");
		return NULL;
	}

	// is edge a valid value?
	//edge -= PY_EVENT_CONST_OFFSET;
	if (edge != RISING_EDGE && edge != FALLING_EDGE && edge != BOTH_EDGE)
	{
		PyErr_SetString(PyExc_ValueError, "The edge must be set to RISING, FALLING or BOTH");
		return NULL;
	}

	if (bouncetime <= 0 && bouncetime != -666)
	{
		PyErr_SetString(PyExc_ValueError, "Bouncetime must be greater than 0");
		return NULL;
	}

	if (timeout <= 0 && timeout != -1)
	{
		PyErr_SetString(PyExc_ValueError, "Timeout must be greater than 0");
		return NULL;
	}

	Py_BEGIN_ALLOW_THREADS // disable GIL
	result = blocking_wait_for_edge(gpio, edge, bouncetime, timeout);
	Py_END_ALLOW_THREADS   // enable GIL

	if (result == 0) {
		Py_RETURN_NONE;
	} else if (result == -1) {
		PyErr_SetString(PyExc_RuntimeError, "Conflicting edge detection events already exist for this GPIO pin");
		return NULL;
	} else if (result == -2) {
		PyErr_SetString(PyExc_RuntimeError, "Error waiting for edge");
		return NULL;
	} else {
		return Py_BuildValue("i", gpio);
	}

}

static int gpio_func_check(int gpio, unsigned char pn []) {
	int f = MODE_UNKNOWN;
	
	switch (gpio)
	{	case 7:
		case 11:
		case 12:
		case 13:
		case 15:
		case 16:
		case 18:
		case 22:
		case 26:
		case 27:
		case 28:
		case 29:
		case 31:
		case 35:
		case 36:
		case 37:
		case 38:
		case 40:
				 if (OUTPUT == gpio_get_dir(gpio)) {
					 f = OUTPUT;
					 memcpy(pn, "gpio(input)", strlen("gpio(input)"));
				 }
				 else if (INPUT == gpio_get_dir(gpio)) {
					f = INPUT;
					memcpy(pn, "gpio(output)", strlen("gpio(output)"));
				 }
				 else if (gpio_get_dir(gpio) < 0) {
					f = MODE_UNKNOWN;
					memcpy(pn, "unkown", strlen("unkown"));
				 }
				 break;

		case 3 :
		case 5 : 
					f = I2C; 
					memcpy(pn, "i2c", strlen("i2c"));
					break;
		case 19 :
		case 21 :
		case 23 :
		case 24 : 
					f = SPI;
					memcpy(pn, "spi", strlen("spi"));
					break;

		case 32 :
		case 33 : 
					f = PWM; 
					memcpy(pn, "pwm", strlen("pwm"));
					break;

		case 8 :
		case 10 : 
					f = SERIAL;
					memcpy(pn, "serial", strlen("serial"));
					break;

		default :
					f = MODE_UNKNOWN;
					memcpy(pn, "NA", strlen("NA"));
					break;
	}

	return f;
}

// python function value = gpio_function(gpio)
static PyObject *py_gpio_function(PyObject *self, PyObject *args, PyObject *kwargs)
{
	int gpio, f = MODE_UNKNOWN;
	int ret, i;
	int gpiocount = -255;
	int found = 0;
	int gpioport = -255;
	unsigned int gpiooffset;
	PyObject *gpiolist = NULL;
	PyObject *gpiotuple = NULL;
	PyObject *tempobj;
	PyObject *func;
	static char *kwlist[] = {"channel", NULL};
	unsigned char pn[20] = {0};

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|O", kwlist, &gpiolist))
		return NULL;

	if (gpiolist == NULL) {  // gpioport kwarg not set
	// do nothing
	}
	else {
		ret = GPIO_Data_check(gpiolist, gpiotuple, &gpioport, &gpiocount);
		if (ret == 1)
			return NULL;
	}

	if (gpioport == -255 && gpiocount == -255) {
		printf("pin\t\tfunc:\n");
		for (i = 1; i < 41; i++) {
			memset(pn, 0, 20);
			f = gpio_func_check(i, pn);
			printf("%d\t\t%s\n", i, pn);
		}
	} else if (gpioport != -255) {
		if (pin_valid(&gpioport)) return NULL;
		printf("pin\t\tfunc:\n");
		memset(pn, 0, 20);
		f = gpio_func_check(gpioport, pn);
		printf("%d\t\t%s\n", gpioport, pn);
	} else {  
		// gpioport was a list/tuple
		printf("pin\t\tfunc:\n");
		for (i = 0; i < gpiocount; i++) {
			if (gpiolist) {
				if ((tempobj = PyList_GetItem(gpiolist, i)) == NULL) {
					return NULL;
				}
			} else { // assume gpiotuple
				if ((tempobj = PyTuple_GetItem(gpiotuple, i)) == NULL) {
					return NULL;
				}
			}

			ret = pin_check(tempobj, &gpioport);
			if (ret == 1)
				return NULL;
			
			memset(pn, 0, 20);
			f = gpio_func_check(gpioport, pn);
			printf("%d\t\t%s\n", gpioport, pn);
		}
	}

	Py_RETURN_NONE;
}

// python function setwarnings(state)
static PyObject *py_setwarnings(PyObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, "i", &gpio_warnings))
		return NULL;

	Py_RETURN_NONE;
}

static const char moduledocstring[] = "Python GPIO module for VisionFive";

PyMethodDef sfv_gpio_methods[] = {
	{"setup", (PyCFunction)py_setup_gpioport, METH_VARARGS | METH_KEYWORDS,
					"***************************************************************\n" \
					"function: setup direction and pull-up pull-down of GPIO pin \n" \
					"usage: \n" \
					"  import VisionFive.gpio as GPIO \n"\
					"  GPIO.setup(pin, GPIO.OUT) \n" \
					"  GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) \n" \
					"  GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_UP) \n" \
					"***************************************************************\n"},

	{"cleanup", (PyCFunction)py_cleanup, METH_VARARGS | METH_KEYWORDS,
					"***************************************************************\n" \
					"function: set default config to GPIO pin \n" \
					"usage: \n" \
					"  import VisionFive.gpio as GPIO \n"\
					"  GPIO.cleanup(37) \n" \
					"  GPIO.cleanup() \n" \
					"***************************************************************\n"},

	{"output", py_output_gpio, METH_VARARGS, 
					"***************************************************************\n"\
					"function: set output level to GPIO pin \n" \
					"usage: \n"	\
					"  import VisionFive.gpio as GPIO \n"\
					"  GPIO.setup(pin, GPIO.OUT) \n" \
					"  GPIO.output(led_pin, GPIO.HIGH) \n" \
					"  GPIO.output(led_pin, GPIO.LOW) \n" \
					"***************************************************************\n"},

	{"input", py_input_gpio, METH_VARARGS, 
					"***************************************************************\n" \
					"function: get input level from GPIO pin \n" \
					"          returns 1, meaning HIGH level; or 0, meaning LOW level\n" \
					"usage: \n"	\
					"  import VisionFive.gpio as GPIO \n"\
					"  IVAL = GPIO.input(pin) \n" \
					"***************************************************************\n"},

	{"setmode", py_setmode, METH_VARARGS, 
					"function: just compatible with RPI CMD \n"},

	{"getmode", py_getmode, METH_VARARGS, 
					"function: just compatible with RPI CMD \n"},

	{"add_event_detect", (PyCFunction)py_add_event_detect, METH_VARARGS | METH_KEYWORDS,
					"***************************************************************\n" \
					"function: enable edge detection for a GPIO pin.\n" \
					"           [callback]   - a callback function for the event (optional)\n" \
					"           [bouncetime] - set bouncetime(unit: millisecond) to avoid jitter \n" \
					"usage: \n" \
					"  import VisionFive.gpio as GPIO \n"\
					"  \n"
					"  def detect(pin, edge_type): \n" \
					"        if (1 == edge_type): \n" \
					"           print('Rising edge is detected') \n" \
					"        elif (2 == edge_type): \n" \
					"           print('Failing edge is detected') \n" \
					"        \n" \
					"  GPIO.add_event_detect(37, GPIO.FALLING, callback=detect, bouncetime=2) \n" \
					"  GPIO.remove_event_detect(37) \n" \
					"  GPIO.add_event_detect(key_pin, GPIO.RISING, callback=detect, bouncetime=2) \n" \
					"  GPIO.remove_event_detect(37) \n"\
					"***************************************************************\n"},

	{"remove_event_detect", py_remove_event_detect, METH_VARARGS,
					"***************************************************************\n" \
					"function: remove edge detection for a GPIO pin\n" \
					"usage: \n" \
					"  please see usage of API  add_event_detect() \n" \
					"***************************************************************\n"},

	{"event_detected", py_event_detected, METH_VARARGS, 
					"***************************************************************\n" \
					"function: query if edge event is detected \n" \
					"          returns 1, meaning edge is detected; 0, meaning edge isn't detected.\n" \
					"usage: \n" \
					"  import VisionFive.gpio as GPIO \n" \
					"  edge_detected_flag = GPIO.event_detected(37) \n" \
					"***************************************************************\n"},

	{"get_detected_event", (PyCFunction)py_get_detected_event, METH_VARARGS | METH_KEYWORDS, 
					"***************************************************************\n" \
					"function: query the edge type after detecting edge \n" \ 
					"          returns 1, meaning rising edge is detected; \n" \
					"                  2, meaning failing edge is detected.\n" \
					"usage: \n" \
					"  import VisionFive.gpio as GPIO \n" \
					"  edge_type = GPIO.get_detected_event(37) \n" \
					"***************************************************************\n"},

	{"add_event_callback", (PyCFunction)py_add_event_callback, METH_VARARGS | METH_KEYWORDS,
					"***************************************************************\n"\
					"function: adding a callback for an event already defined using add_event_detect()\n" \
					"usage: \n" \
					"  import VisionFive.gpio as GPIO \n" \
					"  GPIO.add_event_detect(37, GPIO.FALLING, bouncetime=2) \n" \
					"  GPIO.add_event_callback(37, callback=detect) \n" \
					"***************************************************************\n"},

	{"wait_for_edge", (PyCFunction)py_wait_for_edge, METH_VARARGS | METH_KEYWORDS,
					"***************************************************************\n"\
					"function: wait for an edge. \n" \
					"          Returns the GPIO pin nubmer or None on timeout.\n" \
					"          [bouncetime] - set bouncetime(unit: second) to avoid jitter \n" \
					"          [timeout] - detecting edge event in a time window(unit: millisecond)  \n" \
					"usage: \n" \
					"  import VisionFive.gpio as GPIO \n" \
					"  GPIO.wait_for_edge(37, GPIO.FALLING, bouncetime=2, timeout=5000) \n" \
					"  GPIO.wait_for_edge(37, GPIO.RISING, bouncetime=2) \n" \
					"  Note: the default timeout is -1, meaning waiting until edge event is detected \n"
					"***************************************************************\n"},

	{"gpio_function", (PyCFunction)py_gpio_function, METH_VARARGS | METH_KEYWORDS,
					"***************************************************************\n"\
					"fucntion: query pin fuction (gpio, pwm, serial, i2c, spi)\n" \
					"usage: \n" \
					"  import VisionFive.gpio as GPIO \n" \
					"  #query function of all pins \n"
					"  GPIO.gpio_function() \n"
					"  GPIO.gpio_function(37) \n"
					"***************************************************************\n"},

	{"setwarnings", py_setwarnings, METH_VARARGS, 
					"just compatible with RPI CMD"},
					
	{NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION > 2
static struct PyModuleDef sfvgpiomodule = {
	PyModuleDef_HEAD_INIT,
	"VisionFive._gpio",      // name of module
	moduledocstring,
	-1,
	sfv_gpio_methods
};
#endif

#if PY_MAJOR_VERSION > 2
PyMODINIT_FUNC PyInit__gpio(void)
#else
PyMODINIT_FUNC init_gpio(void)
#endif
{
	int i;
	PyObject *module = NULL;

#if PY_MAJOR_VERSION > 2
	if ((module = PyModule_Create(&sfvgpiomodule)) == NULL)
		return NULL;
#else
	if ((module = Py_InitModule3("VisionFive._gpio", sfv_gpio_methods, moduledocstring)) == NULL)
		return;
#endif

	define_py_constants(module);

	for (i=0; i<41; i++)
		gpio_direction[i] = -1;

	// detect board type
	if (get_vf_info(&VisonFiveinfo))
	{
		PyErr_SetString(PyExc_RuntimeError, "This module can only be run on a VisionFive board!");
#if PY_MAJOR_VERSION > 2
		return NULL;
#else
		return;
#endif
	}

	if (VisonFiveinfo.revision == 7100) {
		GPIO2line = &GPIO2line_VisionFive_v1;
	} else if (VisonFiveinfo.revision == 7110) {
		GPIO2line = &GPIO2line_VisionFive_v2;
	}

	// Add PWM class
	if (PWM_init_PWMType() == NULL)
#if PY_MAJOR_VERSION > 2
		return NULL;
#else
		return;
#endif
	Py_INCREF(&PWMType);
	PyModule_AddObject(module, "PWM", (PyObject*)&PWMType);

#if PY_MAJOR_VERSION < 3
	if (!PyEval_ThreadsInitialized())
		PyEval_InitThreads();
#endif

	if (Py_AtExit(event_cleanup_all) != 0)
	{
#if PY_MAJOR_VERSION > 2
		return NULL;
#else
		return;
#endif
	}

#if PY_MAJOR_VERSION > 2
	return module;
#else
	return;
#endif
}

#include "Python.h"
#include "../gpio/cpuinfo.h"

VisonFive_info VisonFiveinfo;

static const char moduledocstring[] = "Board type For visionfive";

static PyObject* py_get_boardtype(PyObject* self, PyObject *args) {
	int retval = 0;

	if(get_vf_info(&VisonFiveinfo))
	{
		PyErr_SetString(PyExc_RuntimeError, "This module can only be run on a VisionFive board!");
		Py_RETURN_NONE;
	}

	if (VisonFiveinfo.revision == 7100) {
		retval = 1;
	} else if (VisonFiveinfo.revision == 7110) {
		retval = 2;
	}

	return Py_BuildValue("i", retval);
}

static PyMethodDef sfc_boardtype_methods[] = {
	{"boardtype", py_get_boardtype, METH_NOARGS, " Get VisionFive board informations"},
	{NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef sfboardtypemodule = {
	PyModuleDef_HEAD_INIT,
	"VisionFive._boardtype",
	moduledocstring,
	-1,
	sfc_boardtype_methods
};
#endif

#if PY_MAJOR_VERSION >= 3
PyMODINIT_FUNC PyInit__boardtype(void)
#else
PyMODINIT_FUNC init_boardtype(void) 
#endif
{
	PyObject* module = NULL;
#if PY_MAJOR_VERSION >=3 
	module = PyModule_Create(&sfboardtypemodule);
	if(module == NULL)
		return NULL;
#else
	module = Py_InitModule3("VisionFive._boardtype", sfc_boardtype_methods, moduledocstring);
	if(mdoule == NULL)
		return NULL;
#endif

#if PY_MAJOR_VERSION >= 3
	return module;
#else
	return;
#endif

}

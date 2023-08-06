# Copyright (c) 2022-2027 VisionFive
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""
This package provides a Python module to control the GPIO on a VisionFive board.
"""

from setuptools import setup, Extension

classifiers = ['Development Status :: 5 - Production/Stable',
               'Operating System :: POSIX :: Linux',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3.8',
               'Topic :: Software Development',
               'Topic :: Home Automation',
               'Topic :: System :: Hardware']

module_gpio = Extension('VisionFive._gpio', 
                        [
                         'source/gpio/py_gpio.c', 
                         'source/gpio/c_gpio.c',
                         'source/gpio/cpuinfo.c',
                         'source/gpio/py_constants.c', 
                         'source/gpio/gpio-utils.c',
                         'source/gpio/event_gpio.c',
                         'source/pwm/soft_pwm.c',
                         'source/pwm/py_pwm.c',
                         ],
                        extra_compile_args=['-D_GNU_SOURCE'])

module_spi = Extension('VisionFive._spi', 
                       [
                        'source/spi/py_spi.c',
                        'source/spi/spi_dev.c'])

module_i2c = Extension('VisionFive._i2c', 
                       [
                        'source/i2c/c_i2c.c',
                        'source/i2c/py_i2c.c'])

module_boardtype = Extension('VisionFive._boardtype',
                           [
                            'source/gpio/cpuinfo.c',
                            'source/boardtype/py_boardtype.c'])

setup(name             = 'VisionFive.gpio',
      version          = '1.2.9',
      author           = 'VisionFive',
      author_email     = 'support@starfivetech.com',
      description      = 'A module to control VisionFive GPIO ports',
      long_description = open('README.txt').read() + open('CHANGELOG.txt').read(),
      license          = 'MIT',
      keywords         = 'VisionFive GPIO',
      url              = 'http://gitlab.starfivetech.com/Product/Software AE/VisionFive-python-gpio/starfive_gpio',
      classifiers      = classifiers,
      packages         = ['VisionFive', 'VisionFive.gpio', 'VisionFive.spi', 'VisionFive.i2c', 'VisionFive.boardtype', 'VisionFive.sample-code', 'VisionFive.sample-code.lcddemo', 'VisionFive.sample-code.lcddemo.lib', 'VisionFive.sample-code.lcddemo.example'],
      package_data = {"": ["*.bmp", "*.jpg"]},
      ext_modules      = [module_gpio, module_spi, module_i2c, module_boardtype]
      )

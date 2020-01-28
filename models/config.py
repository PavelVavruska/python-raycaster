#  Copyright (c) 2019 Pavel Vavruska
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

class Config(object):

    def __init__(self, fov, is_perspective_correction_on, is_metric_on):
        self.__fov = fov
        self.__is_perspective_correction_on = is_perspective_correction_on
        self.__is_metric_on = is_metric_on

    @property
    def fov(self):
        return self.__fov

    @property
    def is_perspective_correction_on(self):
        return self.__is_perspective_correction_on

    @property
    def is_metric_on(self):
        return self.__is_metric_on

    def set_fov(self, fov):
        self.__fov = fov

    def toggle_perspective_correction_on(self):
        self.is_perspective_correction_on = not self.is_perspective_correction_on

    def toggle_metric_on(self):
        self.__is_metric_on = not self.__is_metric_on




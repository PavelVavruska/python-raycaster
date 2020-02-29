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

    def __init__(
            self,
            fov,
            is_perspective_correction_on,
            is_metric_on,
            pixel_size,
            dynamic_lighting,
            texture_filtering
    ):
        self.__fov = fov
        self.__is_perspective_correction_on = is_perspective_correction_on
        self.__is_metric_on = is_metric_on
        self.__pixel_size = pixel_size
        self.__dynamic_lighting = dynamic_lighting
        self.__texture_filtering = texture_filtering

    @property
    def fov(self):
        return self.__fov

    @property
    def is_perspective_correction_on(self):
        return self.__is_perspective_correction_on

    @property
    def is_metric_on(self):
        return self.__is_metric_on

    @property
    def pixel_size(self):
        return self.__pixel_size

    @property
    def dynamic_lighting(self):
        return self.__dynamic_lighting

    @property
    def texture_filtering(self):
        return self.__texture_filtering

    def set_fov(self, fov):
        self.__fov = fov

    def toggle_perspective_correction_on(self):
        self.__is_perspective_correction_on = not self.is_perspective_correction_on

    def toggle_metric_on(self):
        self.__is_metric_on = not self.__is_metric_on

    def set_pixel_size(self, pixel_size):
        self.__pixel_size = pixel_size

    def increase_pixel_size(self):
        if self.pixel_size < 10:
            self.__pixel_size = self.pixel_size + 1

    def decrease_pixel_size(self):
        if self.pixel_size > 1:
            self.__pixel_size = self.pixel_size - 1

    def toggle_dynamic_lighting(self):
        self.__dynamic_lighting = not self.__dynamic_lighting

    def toggle_texture_filtering(self):
        self.__texture_filtering = not self.__texture_filtering







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


class Map:

    def __init__(self):
        self.__map_base = [
            [10, 10, 10, 10, 10, 10, 12, 12, 12, 12, 12, 12, 12, 12, 14, 14, 14, 14, 14, 14],
            [10, -1,000, -1, -1, 10, 12, -1, -1, -1, -1, -1, -1, 12, 14, -1, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, 10, 12, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, 10, 12, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, 10, 12, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, 10, 12, -1, -1, -1, -1, -1, -1, 12, 14, 14, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, 10, 12, -1, -1, -1, -1, -1, -1, 12, 14, -1, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, 10, 12, -1, -1, -1, -1, -1, -1, 12, 14, -1, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, 10, 12, -1, -1, -1, -1, -1, -1, 12, 14, -1, -1, -1, -1, 14],
            [10, 10, -1, -1, -1, 10, 12, -1, -1, -1, -1, -1, -1, 12, 14, -1, -1, -1, 14, 14],
            [10, -1, -1, -1, -1, 10, 12, -1, -1, -1, -1, -1, -1, 12, 14, -1, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, 10, 12, 11, 11, 11, -1, -1, -1, 12, 14, -1, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, 10, 12, -1, -1, -1, -1, -1, -1, 12, 14, -1, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, 10, 12, -1, -1, -1, -1, -1, -1, 12, 14, 14, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 12, 14, -1, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 12, 14, -1, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 12, 14, -1, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, 10, 12, -1, -1, -1, -1, -1, -1, 12, 14, -1, -1, -1, -1, 14],
            [10, -1, -1, -1, -1, 10, 12, -1, -1, -1, -1, -1, -1, 12, 14, -1, -1,000, -1, 14],
            [10, 10, 10, 10, 10, 10, 12, 12, 12, 12, 12, 12, 12, 12, 14, 14, 14, 14, 14, 14]
        ]
        self.__size_y = len(self.__map_base)
        self.__size_x = len(self.__map_base[0])
        self.__map_effects = [[0]*self.__size_y for i in range(self.__size_x)]

    @property
    def size_x(self):
        return self.__size_x

    @property
    def size_y(self):
        return self.__size_y

    @property
    def data(self):
        return self.__map_base

    def get_at(self, x, y):
        return self.__map_base[y][x]

    def set_at(self, x, y, number):
        self.data[y][x] = number

    def get_effect_at(self, x, y):
        return self.__map_effects[y][x]

    def set_effect_at(self, x, y, number):
        self.__map_effects[y][x] = number

    @property
    def effect_data(self):
        return self.__map_effects
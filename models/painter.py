#  Copyright (c) 2019 Pavel Vavruska
#   Permission is hereby granted, free of charge, to any person obtaining a copy
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
import tkinter


class Painter():
    @classmethod
    def __init__(cls, canvas, pixel_size):
        cls.__canvas = canvas  # type: tkinter.Canvas
        cls.__pixel_size = pixel_size

    @classmethod
    def colored_line(cls, x1, y1, y2, color):
        cls.__canvas.create_rectangle(x1*cls.__pixel_size,
                                y1*cls.__pixel_size,
                                x1*cls.__pixel_size+cls.__pixel_size,
                                y2*cls.__pixel_size, fill=color)
    @classmethod
    def colored_rectangle(cls, x1, y1, color):
        cls.__canvas.create_rectangle(x1*cls.__pixel_size,
                                y1*cls.__pixel_size,
                                x1*cls.__pixel_size+cls.__pixel_size,
                                y1*cls.__pixel_size+cls.__pixel_size, fill=color)
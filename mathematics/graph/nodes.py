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

import logging

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)


class Dijkstra:
    def __init__(self, world_map, start, end):
        self.open_nodes = dict()
        self.closed_nodes = dict()
        self.world_map = []
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.shortest_path = []
        # set start and end points
        self.start_x, self.start_y = start
        self.end_x, self.end_y = end
        _logger.debug('Start: searching for path from ' + str(start) + ' to ' + str(end))
        # create map
        self.world_map = [[-2]*len(world_map) for i in range(len(world_map))]
        for position_y, data_y in enumerate(world_map):
            for position_x, data_x in enumerate(data_y):
                if data_x <= 0:  # not a wall
                    self.world_map[position_y][position_x] = 999

    def get_shortest_path(self):
        _logger.debug('Shortest path (' + str(len(self.shortest_path)) + ') found: ' + str(self.shortest_path))
        return self.shortest_path

    def extract_path_from_closed_nodes(self):
        actual_node = (self.end_y, self.end_x)
        self.shortest_path = [(0, self.end_y, self.end_x)]  # final position
        while (self.start_y, self.start_x) != actual_node:
            length, pos_y, pos_x = self.closed_nodes[actual_node]
            actual_node = (pos_y, pos_x)
            self.shortest_path.append((length, pos_y, pos_x))

    def find_and_mark_neighbours(self):
        if not self.open_nodes:
            _logger.debug('Path found: Open nodes are empty.')
            for key, value in self.closed_nodes.items():
                self.world_map[key[1]][key[0]] = value[0]
            return
        open_nodes_to_close = []
        open_nodes_to_add = dict()
        for key, value in self.open_nodes.items():
            # key[0] = y
            # key[1] = x

            # move node from open to closed
            self.closed_nodes[key] = value
            open_nodes_to_close.append(key)
            self.world_map[key[0]][key[1]] = value[0]

            # add top
            if self.world_map[key[0] + 1][key[1]] == 999:
                open_nodes_to_add[(key[0] + 1, key[1])] = (value[0] + 1, key[0], key[1])

            # add bottom
            if self.world_map[key[0] - 1][key[1]] == 999:
                open_nodes_to_add[(key[0] - 1, key[1])] = (value[0] + 1, key[0], key[1])

            # add right
            if self.world_map[key[0]][key[1] + 1] == 999:
                open_nodes_to_add[(key[0], key[1] + 1)] = (value[0] + 1, key[0], key[1])

            # add left
            if self.world_map[key[0]][key[1] - 1] == 999:
                open_nodes_to_add[(key[0], key[1] - 1)] = (value[0] + 1, key[0], key[1])

        for node in open_nodes_to_close:
            self.open_nodes.pop(node)

        self.open_nodes.update(open_nodes_to_add)

        self.find_and_mark_neighbours()  # next iteration

    def start(self):
        # set start and add it to the open list
        if self.world_map[self.start_y][self.start_x] == 999:
            self.open_nodes[(self.start_y, self.start_x)] = (0, self.start_y, self.start_x)
        else:
            raise ValueError("Start point is not suitable area, it needs to be road")

        if not self.world_map[self.end_y][self.end_x] == 999:
            raise ValueError("End point is not suitable area, it needs to be road")
        self.find_and_mark_neighbours()
        self.extract_path_from_closed_nodes()

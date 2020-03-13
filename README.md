# python-raycaster
POC Python Raycaster on Pygame

Raycaster engine is inspired by 90's PC games. It takes three inputs: 
* 2D array representing the map 
* Player (coordinates, angle of view)

## How to play

* `W / S     - move forward/backward`
* `A / D     - turn left/right`
* `Q / E     - strafe left/right`
* `UP / DOWN - level of detail`
* `P - perspective correction on / off`
* `L - dynamic lighting on / off`
* `Mouse click on minimap - execute move to the selected place by using Dijkstra's Shortest Path First algorithm.`

<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200313.png">
13.03.2020 version - Added object zbuffer and renderer for transparent items in the map


<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200301.png">
01.03.2020 version - Dijkstra's Shortest Path First algorithm for minimap mouse click, dynamic lighting on/off, perspective correction on/off


<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200219.png">
19.02.2020 version - engine migrated from Tkinter to Pygame, big cleanup of code


<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200128.png">
28.01.2020 version - POC Python Tkinter Ray caster

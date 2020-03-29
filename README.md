# python-raycaster
POC Python Raycaster on Pygame

Raycaster engine is inspired by 90's PC games. It takes three inputs: 
* 2D array representing the map 
* Player (coordinates, angle of view)

## How to play
* `G / H     - after mouse select on minimap build/destroy tower`
* `W / S     - move forward/backward`
* `A / D     - turn left/right`
* `Q / E     - strafe left/right`
* deprecated `UP / DOWN - level of detail`
* deprecated `P - perspective correction on / off`
* deprecated `L - dynamic lighting on / off`
* `Mouse click on minimap - execute move to the selected place by using Dijkstra's Shortest Path First algorithm.`

<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200322_2.png">
22.03.2020 version (118bc4dbd1432d8a9ff032ca6f0aa815553f4ee1):


### Features
* removed PIL library from dependencies, using pygame image lib instead
* added scaled images of tarrain to the minimap


<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200322.png">
22.03.2020 version (58697ea11fde85f633341bb4dff89c6a62e46097):


### Features
* `(huge performace increase) rewritten graphics renderer to use native pygame line/rect interface instead of directly interfacing with canvas on pixel basis`
* `tower defense game mechanics`
* `spawning creeps with health and level`
* `building and destroying towers by selecting empty space/tower and using keys G/H`

<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200329.png">
29.03.2020 version - Added POC floor/ceiling


<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200313.png">
13.03.2020 version - Added object zbuffer and renderer for transparent items in the map


<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200301.png">
01.03.2020 version - Dijkstra's Shortest Path First algorithm for minimap mouse click, dynamic lighting on/off, perspective correction on/off


<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200219.png">
19.02.2020 version - engine migrated from Tkinter to Pygame, big cleanup of code


<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200128.png">
28.01.2020 version - POC Python Tkinter Ray caster

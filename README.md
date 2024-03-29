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

<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20230109.png">
9.1.2023 version (d8143365b81375b5ca68592544fd6ab3da7cbf54):

### Features
+ POC floor and ceiling render


<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20221119.png">
19.11.2022 version (405b1bae47b3b76bd0297029ba62814bf6be082b):

### Features
+ Raycasting and texture mapping rewritten into Rust. Result 50x faster.


<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200404.png">
04.04.2020 version (e548d8ef46d51d38eaf9363b63c414a916d9b533):



<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200329.png">
29.03.2020 version (c8df8d6e7a37e62a841591f972fa33e5d198b1f9):


### Features
+ POC floor/ceiling


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


<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200313.png">
13.03.2020 version - Added object zbuffer and renderer for transparent items in the map


<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200301.png">
01.03.2020 version - Dijkstra's Shortest Path First algorithm for minimap mouse click, dynamic lighting on/off, perspective correction on/off


<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200219.png">
19.02.2020 version - engine migrated from Tkinter to Pygame, big cleanup of code


<img alt="Description" src="https://github.com/PavelVavruska/python-raycaster/blob/master/raycaster_20200128.png">
28.01.2020 version - POC Python Tkinter Ray caster

Record working hours on Nokia N9
================================

This simple Python module can be used to compute and record elapsed
times between "logging in" and "logging out" on a mobile device. For
this there is a rudimentary GUI described with qml. The GUI also offers
the possibility of assigning certain projects to the time intervals.

By default at the days when a user logs in, the program expects 7
hours 30 minutes of total work time and computes a total
balance according to this.

At the first run the module creates two json files which are used to
record the times and the default values for the program. From the
latter one, we can change the expected daily time and the project
names. The file of the recorded times shows the most current one at
the top so that it can be viewed easily with a text editor.

The program can be installed simply by copying the codes into an
easily accessible location on the device. The json files will be
created into the same directory.

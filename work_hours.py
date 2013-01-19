#!/usr/bin/python
# -*- coding: utf-8 -*-

# Recording working hours on Nokia N9
# Copyright (C) 2012,2013 Jarno Saarimäki
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
"""
This module creates a rudimentary interface for recording working
hours. It has been tested with Nokia N9, but it should work with minor
changes on any device that has a Python interpreter and the required
Qt4-bindings.

Currently there is no desktop entry for running this script and no way
for installing it. Instead, the script should be placed to an easily
accessible location and when run for the first time (e.g., from the
shell) it will create two json files into the same directory. The
other one will contain the working hours with the most recent ones at
the top and the other one will contain parameters for how the times
are recorded and what projects there exist.

There are also two qml files that specify the GUI. These should be
located in the same folder as this script.
"""
import sys,os,time,json
from PySide import QtCore,QtGui,QtDeclarative,QtOpenGL

#: By default daily working time is 7 hours and 30 minutes
#: This can be overridden in the file *work_setup.py*
DAILY_TIME = [7,30]

#: Setup file for the work
#: Created if it doesn't exist
setup_file = 'work_setup.json'

#: File for the recorded data
#: Created if it doesn't exist
times_file = 'work_times.json'

# # Assume this name for the processor of N9
# # We don't need this knowledge anymore
# if os.uname()[-1] == 'armv7l': onPC = False
# else: onPC = True

def comp_totals(stime,etime,daily_total = None,grand_total = None):
    """
    Compute the total times according to the a start time and an
    endtime. 

    :param stime: start time of a session as string (%H:%M)
    :param etime: end time of a session as string
    :param daily_total: already recorded time fo this date (%H:%M)
    :param grand_total: total recorded time (%H:%M)
    """
    if daily_total != None:
        daily_total = time.strptime(daily_total,'%H:%M')
        hours = daily_total.tm_hour
        mins = daily_total.tm_min
    else: hours,mins = 0,0
    # Convert time strings
    etime = time.strptime(etime,'%H:%M')
    stime = time.strptime(stime,'%H:%M')
    # Add hours and minutes the daily total
    hours += etime.tm_hour - stime.tm_hour
    mins += etime.tm_min - stime.tm_min    
    if mins < 0:
        mins += 60
        hours -= 1        
    # Get grand total with the correct sign
    gt_sign = 1
    if grand_total != None:
        if grand_total[0] == '-':
            grand_total = time.strptime(grand_total,'-%H:%M')
            gt_sign = -1
        else:
            grand_total = time.strptime(grand_total,'%H:%M')
    else:
        grand_total = time.strptime('00:00','%H:%M')
    # Add the daily hours and minutes to the grand total
    # Take into accound the scheduled daily time 
    grand_in_min = gt_sign*grand_total.tm_min + \
                   gt_sign*grand_total.tm_hour*60
    grand_in_min += mins-DAILY_TIME[1]+hours*60-DAILY_TIME[0]*60
    # Hours
    grand_hours = grand_in_min // 60
    # If negative hours we have add 1
    if grand_hours < 0:    grand_hours += 1
    # Subract the hours from the mins
    grand_mins = abs(grand_in_min - grand_hours*60 )
    # With negative times it is possible to have 60 mins
    if grand_in_min < 0 and grand_mins == 60:
        grand_mins = 0
        grand_hours -= 1
    # Convert the totals back to strings
    grand_total = '%02d:%02d' % (grand_hours,grand_mins)
    if grand_in_min < 0 and grand_hours == 0:
        grand_total = '-' + grand_total

    daily_total = '%02d:%02d' % (hours,mins)
    
    return daily_total, grand_total

class Writeread(QtCore.QObject):
    """
    Read and write the working hours in file "work_times.json".
    """
    def __init__(self,parent=None):
        """Constructor"""
        super(Writeread, self).__init__(parent)
        # By default set that a session is not started
        self.is_logged_in = False
        # The file that is used to save the data
        self.filename = times_file
        if os.path.exists(self.filename):
            with open(self.filename,'r') as f:
                self.hours = json.load(f)
        else:   self.hours = []
        # Check if there is already an entry for today
        if len(self.hours) and self.hours[0]['date'] == time.strftime('%D'):
            # Check if a session is already started
            if len(self.hours[0]['times']) > 0 and \
                len(self.hours[0]['times'][-1]) == 1:
                self.is_logged_in = True
        # Otherwise add an entry for today
        else:            
            self.hours.insert(0,{'date': time.strftime('%D'),
                                 'times': [],
                                 'daily total' : None,
                                 'grand total' : None} )
    @QtCore.Slot(result=str)
    def log_in(self):
        """Logging in."""
        if self.is_logged_in:
            return unicode('Already logged in at %s' % 
                           self.hours[0]['times'][-1][0])
        # Get the time
        self.hours[0]['times'].append([time.strftime('%H:%M')])
        self.is_logged_in=True
        # Write the file
        with open(self.filename,'w') as f:
            json.dump(self.hours,f,indent=2)
        return unicode('Successfully logged in at %s' % 
                           self.hours[0]['times'][-1][0])

    @QtCore.Slot(result=str)
    def log_out(self):
        """Logging out."""
        if not self.is_logged_in:
            return unicode('Not logged in')
        # Get the time
        etime = time.strftime('%H:%M')
        # If there is grand total for the previous day
        try: grand_total = self.hours[1]['grand total']
        except: grand_total = None
        # Compute the total according to this session
        self.hours[0]['daily total'], self.hours[0]['grand total'] = \
            comp_totals( self.hours[0]['times'][-1][0] , etime ,
                         self.hours[0]['daily total'], grand_total  )
        # Write the end time to the file
        self.hours[0]['times'][-1].insert(1,etime)
        self.is_logged_in=False
        # Write the file
        with open(self.filename,'w') as f:
            json.dump(self.hours,f,indent=2)
        return unicode('Successfully logged out at %s' % 
                           self.hours[0]['times'][-1][1] )

    @QtCore.Slot(QtCore.QObject,result=str)
    def set_project(self,project):
        """
        Assign a project to the current session.
        """
        if not self.is_logged_in:
            return unicode('not logged in!')
        self.hours[0]['times'][-1].insert(2,project.name)
        with open(self.filename,'w') as f:
            json.dump(self.hours,f,indent=2)
        return unicode('project %s successfully chosen' % project.name)

    @QtCore.Slot(result=str)
    def welcomemsg(self):
        """
        Produce a welcome string at the start.
        """
        if self.is_logged_in:
            return unicode('Last logged in at %s' %
                self.hours[0]['times'][-1][0])
        else:
            return unicode('Log in to start a session')

class ProjectListModel(QtCore.QAbstractListModel):
    """
    Model for project list that can be accessed from the qml
    interface.
    """
    COLUMNS = ('project',)

    def __init__(self,projects):
        QtCore.QAbstractListModel.__init__(self)
        self.projects = projects 
        self.setRoleNames(dict(enumerate(ProjectListModel.COLUMNS)))

    def rowCount(self,parent=QtCore.QModelIndex()):
        return len(self.projects)

    def data(self, index, role):
        if index.isValid() and \
            role == ProjectListModel.COLUMNS.index('project'):
            return self.projects[index.row()]

class Project(QtCore.QObject):
    """
    Class for a project.
    """
    def __init__(self,name):
        super(Project,self).__init__()
        self.name = name
    def __str__(self):
        return 'Project "%s"' % (self.name)

if __name__ == "__main__":
    # Set this directory to be the current one
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # Read or create the setup data
    if os.path.exists(setup_file):
        with open(setup_file,'r') as f:
            work_setup = json.load(f)
        projects = work_setup['projects']
        DAILY_TIME = work_setup['daily_time']
    else:
         projects = ['Project1','Project2','Project3',
                     'Project4','Project5','Project6']
         work_setup = dict(projects=projects,daily_time=DAILY_TIME)
         with open(setup_file,'w') as f:
            json.dump(work_setup,f,indent=2)
    # Assign the project instances
    projects = [Project(proj) for proj in projects]
    # Start the app
    app = QtGui.QApplication(sys.argv)
    view = QtDeclarative.QDeclarativeView()
    # Use OpenGL
    glw = QtOpenGL.QGLWidget()
    view.setViewport(glw)
    # Connect the required functions to the qml object
    context = view.rootContext()
    writeread = Writeread()
    context.setContextProperty('writeread', writeread)
    projectList = ProjectListModel(projects)
    context.setContextProperty('ProjectListModel', projectList)
    # Set the qml source
    view.setSource('main.qml')
    view.showFullScreen()
    # Exit the interpreter when done
    sys.exit( app.exec_() )

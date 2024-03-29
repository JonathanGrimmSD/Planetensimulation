#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division



__author__ = "Jonathan Grimm"
__date__ = "12.06.18"
__IDE__ = "PyCharm Community Edition"

import scipy.constants as constants
import time
from PlanetVector import Vector
import math
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QObject


class Calculations(QObject):

    def __init__(self, universe, settings,parent=None):
        QObject.__init__(self, parent=parent)
        self.universe = universe
        self.runtime = True
        self.time1 = 0
        self.time2 = 0
        self.deltaT = 0

        self.settings = settings

    def run(self):
        self.time1 = time.time()
        steps = 0
        while self.runtime:
            time.sleep(0.00000000001)
            steps += 1
            steplimit = 10
            if steps > steplimit:
                steps = 0
            self.time2 = time.time()
            self.deltaT = self.time2 - self.time1
            self.time1 = self.time2
            for so0 in self.universe:
                # if so0.name!="earth":
                self.calculations(so0)
            # self.calculations(universe[1])

            for so in self.universe:

                so.x = so.xnew
                so.y = so.ynew
                so.velocityVector = so.vVnew
                so.pv = Vector(so.x, so.y)
                so.drawx = (so.x - self.settings.focus.x) * self.settings.proportion_scaling + self.settings.scaling[
                    0] - so.radius / 2
                so.drawy = (so.y - self.settings.focus.y) * self.settings.proportion_scaling + self.settings.scaling[
                    1] - so.radius / 2

                if self.settings.trajectory and steps >= steplimit:

                    if self.settings.heliocentric is False:
                        traj = np.array([so.x, so.y])
                        traj = traj - (self.settings.focus.x, self.settings.focus.y)
                        traj = traj * self.settings.proportion_scaling + self.settings.scaling[0]
                    else:
                        traj = np.array([so.x, so.y])
                        traj = (traj) * \
                               self.settings.proportion_scaling + self.settings.scaling[0]

                    so.trajectory.append(QtCore.QPointF(*traj))
                    so.trajectory2.append(QtCore.QPointF(*traj))
                    if self.settings.heliocentric:
                        so.trajectory2=[]
                        for p in so.trajectory:
                            so.trajectory2.append(QtCore.QPointF(p.x()+(self.universe[0].x-self.settings.focus.x)
                                                                 *self.settings.proportion_scaling,
                                                                 p.y()+(self.universe[0].y-self.settings.focus.y)
                                                                 *self.settings.proportion_scaling))
                            #p.setX(p.x())
                            #p.setY(p.y())
                            #p.setX(p.x()-self.settings.focus.x*self.settings.proportion_scaling/100 )
                            #p.setY(p.y()-self.settings.focus.y*self.settings.proportion_scaling/100 )
                            #print a0,p.x()
                            pass

                    if len(so.trajectory) > self.settings.traj_length:
                        del so.trajectory[0]

    def calculations(self, so0):
        total_accel_vector = Vector()
        for so1 in self.universe:
            if so0 != so1:
                zaehler = so1.pv - so0.pv
                nenner = math.pow(zaehler.getnorm(), 3)
                temp = zaehler / nenner
                temp = temp * so1.mass
                total_accel_vector = total_accel_vector + temp

        # beschleunigungsvektor: a_neu = m * G
        total_accel_vector = total_accel_vector * constants.G
        # geschwindigkeitsvektor: v_neu = a_neu * dt
        total_velocity_vector = total_accel_vector * (self.deltaT * self.settings.time_scale)

        # Addiere den alten und den neuen Geschwindigkeitsvektor: temp = v_alt + v_neu
        temp = so0.velocityVector + total_velocity_vector
        # if so0.name=="earth":
        so0.vVnew = temp

        so0.xnew = so0.x + (so0.vVnew.x() * (self.deltaT * self.settings.time_scale))
        so0.ynew = so0.y + (so0.vVnew.y() * (self.deltaT * self.settings.time_scale))

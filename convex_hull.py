from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))


import time
import numpy as np

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25

#
# This is the class you have to complete.

class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False
		
# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)
		
	def eraseHull(self,polygon):
		self.view.clearLines(polygon)
		
	def showText(self,text):
		self.view.displayStatusText(text)


	# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points, pause, view):
		self.pause = pause
		self.view = view
		assert(type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()

		# TODO: SORT THE POINTS BY INCREASING X-VALUE
		increasingX = sorted(points, key=lambda point: point.x())

		t2 = time.time()

		t3 = time.time()
		# this is a dummy polygon of the first 3 unsorted points
		#polygon = [QLineF(points[i],points[(i+1)%3]) for i in range(3)]
		#polygon = self.divideAndConquer(increasingX, pause, view)
		polygon = self._divide_conquer(increasingX, pause, view)
		# TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
		t4 = time.time()

		hull = [QLineF(polygon[i], polygon[(i+1) % np.size(polygon)])
                    for i in range(np.size(polygon))]

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(hull,RED)
		print('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))

	def _divide_conquer(self, myPoints, pause, view):
		#get size of list
		listSize = np.size(myPoints)

		#check for small points graph
		if (listSize == 1):
			return myPoints

		#declare a value to split around
		midVal = listSize // 2
		#find left side points
		leftSide = self._divide_conquer(myPoints[:midVal], pause, view)
		#get right side points
		rightSide = self._divide_conquer(myPoints[midVal:], pause, view)

		#another check for small graph (with only 2 points)
		if np.size(leftSide) == 1 and np.size(rightSide) == 1:
			leftSide.extend(rightSide)
			return leftSide

		#O(n)->
		rightPlaceholder = rightSide.index(min(rightSide, key=lambda rightPoint: rightPoint.x()))
		leftPlaceholder = leftSide.index(max(leftSide, key=lambda leftPoint: leftPoint.x()))


		#O(n) time (get high point)
		i = leftPlaceholder
		j = rightPlaceholder
		leftTestVal = True
		rightTestVal = True
		curve = (rightSide[j].y() - leftSide[i].y()) / \
				(rightSide[j].x() - leftSide[i].x())
		while leftTestVal or rightTestVal:
			leftTestVal = False
			rightTestVal = False
			while True:
				updatedCurve = (rightSide[j].y() - leftSide[(i - 1) % np.size(leftSide)].y()) / (
						rightSide[j].x() - leftSide[(i - 1) % np.size(leftSide)].x())
				if updatedCurve < curve:
					leftTestVal = True
					curve = updatedCurve
					i = (i - 1) % np.size(leftSide)
				else:
					break
			while True:
				updatedCurve = (rightSide[(j + 1) % np.size(rightSide)].y() - leftSide[i].y()) / (
						rightSide[(j + 1) % np.size(rightSide)].x() - leftSide[i].x())
				if updatedCurve > curve:
					rightTestVal = True
					curve = updatedCurve
					j = (j + 1) % np.size(rightSide)
				else:
					break
		topPoint = (i, j)

		#O(n) time (get low point)
		i = leftPlaceholder
		j = rightPlaceholder
		leftTestVal = True
		rightTestVal = True
		curve = (rightSide[j].y() - leftSide[i].y()) / \
				(rightSide[j].x() - leftSide[i].x())
		while leftTestVal or rightTestVal:
			leftTestVal = False
			rightTestVal = False
			while True:
				updatedCurve = (rightSide[j].y() - leftSide[(i + 1) % np.size(leftSide)].y()) / (
						rightSide[j].x() - leftSide[(i + 1) % np.size(leftSide)].x())
				if updatedCurve > curve:
					leftTestVal = True
					curve = updatedCurve
					i = (i + 1) % np.size(leftSide)
				else:
					break
			while True:
				updatedCurve = (rightSide[(j - 1) % np.size(rightSide)].y() - leftSide[i].y()) / (
						rightSide[(j - 1) % np.size(rightSide)].x() - leftSide[i].x())
				if updatedCurve < curve:
					rightTestVal = True
					curve = updatedCurve
					j = (j - 1) % np.size(rightSide)
				else:
					break

		bottomPoint = (i, j)

		if pause:
			self.displayRecursion(leftSide, rightSide, topPoint, bottomPoint)

		#COMBINE! O(n)
		returnList = []
		lowVal = bottomPoint[0]
		returnList.append(leftSide[lowVal])
		while lowVal != topPoint[0]:
			lowVal = (lowVal + 1) % np.size(leftSide)
			returnList.append(leftSide[lowVal])
		upperVal = topPoint[1]
		returnList.append(rightSide[upperVal])
		while upperVal != bottomPoint[1]:
			upperVal = (upperVal + 1) % np.size(rightSide)
			returnList.append(rightSide[upperVal])
		self.displayRecursion(leftSide, rightSide, topPoint, bottomPoint)
		return returnList

	def displayRecursion(self, left, right, upperTangent, lowTangent):
		leftDisplay = [QLineF(left[i], left[(i + 1) % np.size(left)]) for i in range(np.size(left))]
		rightDisplay = [QLineF(right[i], right[(i + 1) % np.size(right)]) for i in range(np.size(right))]
		upperDisplay = QLineF(left[upperTangent[0]], right[upperTangent[1]])
		lowerDisplay = QLineF(left[lowTangent[0]], right[lowTangent[1]])

		self.showHull(leftDisplay, RED)
		self.showHull(rightDisplay, RED)

		self.showTangent([upperDisplay, lowerDisplay], BLUE)

		self.eraseHull(leftDisplay)
		self.eraseHull(rightDisplay)

		self.eraseTangent([upperDisplay, lowerDisplay])





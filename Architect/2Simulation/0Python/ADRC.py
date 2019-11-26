import numpy as np
import matplotlib.pyplot as plt
import math
import random


# sign function
def sign(val):
	
	if val>1e-6:
		val  = 1
	elif val < -1e-6:
		val = -1
	else:
		val = 0

	return val

#zone-functon
# return 0: in side
# return +/- 1:outside
def fsg(x,d):

	output = (sign(x+d) - sign(x-d))/2

	return output

#power function
def fal(e,alpha,zeta):

	s = fsg(e,zeta)

	fal_output = e*s/(pow(zeta,1-alpha))+pow(abs(e),alpha)*sign(e)*(1-s)

	return fal_output

#
#class td filter
#
class ADRC_TD():

	"""docstring for Td_filter"""
	def __init__(self,r,h,N0,c):
		self.r = r
		self.h = h
		self.N0 = N0
		self.c = c
		self.h0 = 0.0
		self.fh = 0.0
		self.x1 = 0.0
		self.x2 = 0.0
		self.fh = 0.0

	#
	# TD tracker(Second-Order)
	#
	# x1(k+1) = x1(k) + h * x2(k)
	# x2(k+1) = x2(k) - r0 * u(k)
	# fhan(x1,x2,r0,h0)

	def fhan(self,excpt):
		# Calculate the error between original signal and excepted signal.
		x1_delta = self.x1 - excpt
		# Optimized step value.
		self.h0 = self.N0 * self.h
		# Calulate d and a0
		# d means the limited increment of r
		# a0 means the increment of x2
		d = self.r * self.h0 * self.h0
		a0 = self.x2 * self.h0
		# Optimized delta
		y = x1_delta + a0
		
		# a1 means limit of delta
		# a2 means optimized delta based x2
		a1 = math.sqrt(d*(d+8*abs(y)))
		a2 = a0 + sign(y)*(a1-d)/2

		# Calculate the final delta of x2 :a.
		# If outof d, a is a2
		# If inside d, a is a0+y
		a = (a0 + y)*fsg(y,d) + a2*(1 - fsg(y,d))

		# Calculate the final delta of x2.
		# If outof d, the increment of x2 is r*sign(a)
		# If inside d, a is r*(a/d)
		self.fh = -self.r * (a/d) * fsg(a,d) - self.r * sign(a)*(1-fsg(a,d))

		# Update x1 by x2,and x2 by fh
		self.x1 = self.x1 + self.h * self.x2
		self.x2 = self.x2 + self.h * self.fh

#
#class ESO
#
class ADRC_ESO():
	"""docstring for ADRC_ESO"""
	def __init__(self,beta01,beta02,beta03,z1,b0):
		self.beta01 = beta01
		self.beta02 = beta02
		self.beta03 = beta03
		self.b0 = b0
		self.e = 0.0
		self.z1 = 0.0
		self.z2 = 0.0
		self.z3 = 0.0
		self.y = 0.0
		self.b = 0
		self.u = 0

	def fleso(self):
		self.e = self.z1 - self.y
		#update observe
		self.z1 += self.z2 - self.beta01 * self.e
		self.z2 += self.z3 - self.beta02 * self.e + self.b * self.u
		self.z3 += -self.beta03*self.e

#
#class NL
#
class ADRC_NL():
	"""docstring for ADRC_NL"""
	def __init__(self,beta0,beta1,beta2,N1,C,alpha1,alpha2,zeta,b):
		self.beta0 = beta0
		self.beta1 = beta1
		self.beta2 = beta2
		self.N1 = N1
		self.C = C
		self.alpha1 = alpha1
		self.alpha2 = alpha2
		self.zeta = zeta
		self.b = b

def graph_display(plot,xnums,ynums,ID,xval,yval,name,xlabs,ylabs,color):
	ax = plot.add_subplot(xnums,ynums,ID)
	ax.set_xlabel(xlabs)
	ax.set_ylabel(ylabs)
	ax.plot(xval, yval, color=color, label=name)
	ax.legend()

#
#Setup function
#
def setup():
	
	w0 = 1
	b1 = 3*w0
	b2 = 3*w0*w0
	b3 = w0*w0*w0
	print('b1=%f,b2=%f,b3=%f' %(b1,b2,b3))
	
	#r h N0 C
	td = ADRC_TD(300000.0,0.01,5.0,1.0);
	
	#set cycle times
	size=500

	#set X axis value
	X  = np.array(range(0,size))

	#TD
	Y_TD_h0  = np.array(range(size), dtype = float)
	Y_TD_a0  = np.array(range(size), dtype = float)
	Y_TD_s   = np.array(range(size), dtype = float)
	Y_TD_fh  = np.array(range(size), dtype = float)
	Y_TD_x1  = np.array(range(size), dtype = float)
	Y_TD_x2  = np.array(range(size), dtype = float)
	Y_TD_fh  = np.array(range(size), dtype = float)

	for k in np.arange ( size ):
		Y_TD_s[k]  = 1000*math.sin(k%180/57.29) + random.randint(-200,200)
		#execute td
		td.fhan(Y_TD_s[k])

		Y_TD_h0[k] = td.h0
		Y_TD_fh[k] = td.fh
		Y_TD_x1[k] = td.x1
		Y_TD_x2[k] = td.x2
		Y_TD_fh[k] = td.fh

	fig = plt.figure()
	graph_display(fig,3,2,1,X,Y_TD_fh,"TD fh","cycle time","rate",'red')
	graph_display(fig,3,2,5,X,Y_TD_x1,"TD x1","cycle time","rate",'red')
	graph_display(fig,3,2,5,X,Y_TD_s,"TD signal","cycle time","rate",'green')
	graph_display(fig,3,2,3,X,Y_TD_x2,"TD x2","cycle time","rate",'red')
	plt.show()


if __name__ == "__main__":
	setup()

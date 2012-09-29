#!/usr/bin/env python

# ---------------------------------------------------------------------------
#
# FH Wedel, Sommersemester 2012
# 
# Learning & Softcomputing Project
# 
# SVM Training Tool
#
# By:
#	Julian Hille
#	Christian Kulpa
#	Hanno Sternberg
#
# Tree based SVM cross Validataion
#
# ---------------------------------------------------------------------------

import io
import time
import crossValidator
from Options import Options
from libSVMConnector import train, scale, subset
from utils import log
	
def countSetSize(file):
	"""
	Count the number of entries in a set
	
	@type	file: String
	@param	file: Name of the subset
	
	@rtype:		Number
	@return:	Size of the set
	"""
	try:
		f = open(file,"r")
		i = 0
		for l in f:
			i = i+1
		f.close()
	except IOError as e:
		log("An error has occured while try to open file {}".format(file))
		log("{}: {}".format(e.errno, e.strerror))
		exit(1)
	return i

		
def subsetFilename(file,n):
	"""
	Generates a name for a subset.
	
	@type	file: String
	@param	file: Name of the dataset
	
	@type	n: Number
	@param	n: Number of the subset 
	
	@rtype:		String
	@return:	Subset filename
	"""
	return ("{0}.subset_{1}".format(file,n))
	
def dataSetFilename(file,n):
	"""
	Generates a name for a dataset.
	
	@type	file: String
	@param	file: Name of the dataset
	
	@type	n: Number
	@param	n: Number of the subset 
	
	@rtype:		String
	@return:	dataset filename
	"""
	if (n > 0):
		return ("{0}_{1}".format(file,n))
	else:
		return file		
		
def restSetFilename(file,n):
	"""
	Generates a name for a restset.
	
	@type	file: String
	@param	file: Name of the dataset
	
	@type	n: Number
	@param	n: Number of the subset 
	
	@rtype:		String
	@return:	restset filename
	"""
	return dataSetFilename(file,n+1)
	
def genCurSubset(opts, n, size):
	"""
	Generates the n-th subset.
	
	@type	opts: Options
	@param	opts: Options object
	
	@type	n: Number
	@param 	n: Number of the subset
	
	@type	size: Number
	@param	size: Size of the subset
	
	@rtype:		(String, String)
	@return:	Tupel with sub- and restset
	"""
	dataset =dataSetFilename(opts.training_file, n)
	sub = subsetFilename(opts.training_file, n)
	rest = restSetFilename(opts.training_file, n)
	subset(opts, size, dataset, sub, rest)
	return (sub,rest)
	
def crossValidationRound(opts):
	"""
	Generates the n-th subset.
	
	@type	opts: Options
	@param	opts: Options object
	
	@rtype:		[(Number, Number, Number)]
	@return:	Array of best Cs, Gammas and rates for the each subset-SVM
	"""
	if (opts.division_depth > 0):
		cnt = countSetSize(opts.training_file)
		size = cnt / pow(opts.division_factor, opts.division_depth)
		if (size < opts.subset_size):
			size = opts.subset_size
		n = cnt/size
		#log("Total {0}, creating {0} subsets with size {1}".format(cnt, n, size))
		i = 0
		res = []
		totaltime = 0
		remtime = 0
		log("Number of Subset: {}".format(n))
		while i < n:
			sub,rest = genCurSubset(opts, i, size)
			starttime = time.time()
			c,g,rate = crossValidator.validate(opts, sub)
			cvtime = time.time() - starttime
			totaltime += cvtime
			remtime = (totaltime / (i+1))*(n-i)
			res.append((c,g,rate))
			i = i+1
			log("Subset {:03d}: C={:.3f} gamma={:.3f} rate={:.3f} ({}/{})".format(i,c,g,rate,time.strftime("%H:%M:%S", time.gmtime(cvtime)),time.strftime("%H:%M:%S", time.gmtime(remtime))))
		return res
	else:
		c,g,rate = crossValidator.validate(opts, opts.training_file)
		log("Best C: {}, Best Gamma: {}, Rate: {}".format(c,g,rate))
		return [(c,g,rate)]

def calcNewRange(res,opts):
	"""
	Calculates the range of c and gamma, based on return values of the subset crossvalidations.
	
	@type	res: [(Number, Number, Number)]
	@param	res: Array with cross validation return values
	
	@type	opts: Options
	@param	opts: Options object
	
	@rtype:		(Number, Number, Number, Number)
	@return:	Tupel with new min and max values for c and gamma
	"""
	cmax,cmin,cs = opts.c_range
	gmax,gmin,gs = opts.g_range
	clb,cub,csb = opts.c_range_max # Lower and upper boundaries for c
	glb,gub,gsb = opts.g_range_max # Lower and upper boundaries for g
	if cs < 0:
		cmax,cmin = cmin,cmax
		cub,clb = clb,cub
	if gs < 0:
		gmax,gmin = gmin,gmax
		gub,glb = glb,gub
	for r in res:
		c,g,rate = r
		if (c < cmin and c >= clb):
			cmin = c
		if (c > cmax and c <= cub):
			cmax = c
		if (g < gmin and g >= glb):
			gmin = g
		if (g > gmax and g <= gub):
			gmax = g
	
	if ((cs > 0 and cmin > cmax) or (cs < 0 and cmin > cmax)):
			cmin,cmax = cmax,cmin
	if ((gs > 0 and gmin > gmax) or (gs < 0 and gmin > gmax)):
			gmin,gmax = gmax,gmin
			
	if cs < 0:
		cmax,cmin = cmin,cmax
	if gs < 0:
		gmax,gmin = gmin,gmax			
			
	return cmin,cmax,gmin,gmax

def crossValidate(opts):
	"""
	Starts the tree cross validation.
	The subset tree has a depth defined by the the division-depth opttion.
	Each dataset will be split into a number of subsets defined by the division-factor option.
	
	@type	opts: Options
	@param	opts: Options object
	"""
	totaltime = time.time()
	opts.training_file = scale(opts, opts.training_file)
	log("Scaling input data")
	while opts.division_depth >= 0:
		starttime = time.time()
		log("Range: C={0}; gamma={1}".format(opts.c_range,opts.g_range))
		res = crossValidationRound(opts)
		cstart,cstop,cstep = opts.c_range
		gstart,gstop,gstep = opts.g_range
		cmin,cmax,gmin,gmax = calcNewRange(res, opts)
		opts.division_depth = opts.division_depth -1
		opts.c_range = cmin,cmax,cstep
		opts.g_range = gmin,gmax,gstep
		endtime = time.time()
		log("Time for this round: {0}".format(time.strftime("%H:%M:%S", time.gmtime(endtime-starttime))))
		log("Remaining division steps: {0}".format(opts.division_depth+1))
		
	log("Total time: {}".format(time.strftime("%H:%M:%S", time.gmtime(time.time()-totaltime))))
			
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
# libSVM Connector
#
# ---------------------------------------------------------------------------

from Options import Options
from utils import log
from subprocess import *
	
def train(opts, c= None, g=None, f=None):
	"""
	Trains a given svm
	
	@type	opts: Options
	@param	opts: options object
	"""
	if c == None:
		c = 2**opts.c_value
	if g == None:
		g = 2**opts.g_value
	if f == None:
		f = opts.training_file
	if opts.model_file == None:
		m = ""
	else:
		m = opts.model_file
	file = scale(opts,f)
	#cmd = '"{0}" -c {1} -g {2} {5} "{3}" "{4}"'.format(
	#	opts.svm_train_path, c, g, f, m, opts.additional_arguments)
	#log(cmd)
	return Popen([opts.svm_train_path, "-c", str(c), "-g", str(g), "-v", str(opts.fold), file, m], shell = False, stdout = PIPE).stdout
	#return Popen(cmd, shell = True, stdout = PIPE).stdout
	

def scale(opts, file):
	"""
	Scale the input data
	
	@type	opts: Options
	@param	opts: Options object
	
	@type	file: String
	@param	file: input file to scale
	
	@rtype:		String
	@return:	Name of the file with scaled data
	"""
	#cmd = '"{0}" {3} "{1}" > "{2}"'.format(opts.svm_scale_path, file, file+".scale", opts.additional_arguments)
	#log(cmd)
	try:
		f = open(file+".scale","w",0)
		hnd = Popen(["cmd.exe", "/C", opts.svm_scale_path, file], stdout = PIPE, shell=False).stdout
		for l in hnd.readlines():
			if l == None:
				break
			f.write(l)
		f.close()
	except IOError as e:
		log("An error has occured while try to open file {}".format(file))
		log("{}: {}".format(e.errno, e.strerror))
		exit(1)
	#Popen(cmd, shell=True, stdout=PIPE).wait()
	return file+".scale"

def subset(opts, size, dataset, subset, restset):
	"""
	Generates a subset from a dataset.
	
	@type	opts: Options
	@param	opts: Options object
	
	@type	size: Number
	@param	size: Size of the subset
	
	@type	dataset: String 
	@param	dataset: Filename of the dataset
	
	@type	subset: String
	@param	subset: Filename for the subset
	
	@type	restset: String
	@param	restset: Filename for the restset
	"""
	#cmd = 'python "{0}" "{1}" {2} "{3}" "{4}"'.format(opts.subset_py, dataset, size, subset, restset)
	#log(cmd)
	Popen(["cmd.exe", "/C", "python", opts.subset_py, dataset, str(size), subset, restset], shell = False, stdout = PIPE).wait()
	#Popen(cmd, shell = True, stdout = PIPE).wait()
	
def predict(opts):
	"""
	Predicts the quality of the svm
	
	@type	opts: Options
	@param	opts: Options object
	"""
	cmd = '"{0}" {4} "{1}" "{2}" "{3}"'.format(opts.svm_predict_path, opts.test_file, opts.model_file, opts.output_file, opts.additional_arguments)
	#log(cmd)
	result = Popen([opts.svm_predict_path, opts.test_file, opts.model_file, opts.output_file], shell = False, stdout = PIPE).stdout
	#result = Popen(cmd, shell=True, stdout=PIPE).stdout
	for line in result.readlines():
		log(line)
	
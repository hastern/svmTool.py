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
# Command-Line options parser
#
#
#
# ---------------------------------------------------------------------------

import sys
import utils
import os
import argparse

class Options:
	"""
	Options object, can parse available options from arguments 
	and ask for missing ones.
	"""
	os = ""
	"""Operating system"""
	exec_ext = ""
	"""Extensions for executables (OS-depended)"""
	path_sep = "/"
	"""operation dependet pah seperation"""
	cwd = ""
	"""Current working directory"""
	shell = True
	"""Run commands as a shell"""
	
	libsvm_path = "."
	"""Path to libsvm"""
	svm_scale_path = libsvm_path + "/svm-scale"
	"""Path to libsvm-scale executable"""
	svm_train_path = libsvm_path + "/svm-train"
	"""Path to libsvm-train executable"""
	svm_predict_path = libsvm_path + "/svm-predict"
	"""Path to libsvm-predict executable"""
	subset_py = libsvm_path + "/tools/subset.py"
	"""Path to subset tool from libsvm"""
	gnuplot_path = "."
	"""Path to gnuplot"""
	subset_size = 1
	"""Size of the subset"""
	division_depth = 1
	"""Depth of the division tree"""
	division_factor = 2
	"""Number of childs in the subdivision tree"""
	fold = 5
	"""Number of folds for cross validation (see libsvm-train arguments for more information on this parameter)"""
	worker = 1
	"""Number of local workers (=Threads)"""
	c_range = (0,0,0)
	"""Range for C (start, stop, step)"""
	g_range = (0,0,0)
	"""Range for gamma (start, stop, step)"""
	c_value = 1
	"""Value for kernel parameter C"""
	g_value = 1
	"""Value for kernel parameter gamma"""
	training_file = None
	"""Name of the trainingfile"""
	test_file = None
	"""Name of the testfile"""
	model_file = None
	"""Name of the modelfile"""
	output_file = None
	"""Name of the outputfile"""
	action = ""
	"""Action"""

	additional_arguments = ""
	"""Additional argmuments for libSVM tools"""
	
	
	
	def _actionRequiresOption(self, action, option):
		"""
		test if a given option is required by an action
		
		@type 	action: String
		@param	action: Action
		
		@type	option: String
		@param	option: Option
		
		@rtype	Boolean
		@return	True, if the action requires the given option
		"""
		if (action == "crossValidation"):
			return option in ["libsvmpath","crange","grange","trainingfile"]
		if (action == "train"):
			return option in ["libsvmpath","cvalue","gvalue","trainingfile","modelfile","outputfile"]
		if (action == "test"):
			return option in ["libsvmpath","testfile","modelfile","outputfile"]
		if (action == "merge"):
			return False
		if (action == "subset"):
			return option in ["libsvmpath","trainingfile","outputfile","subsetsize"]
		if (action == "gui"):
			return False
		return False
		
		
	def __init__(self):
		"""
		Initialises the object
		
		@type	self: Options
		@param 	self: Options object
		"""
		self.os = sys.platform
		self.cwd = os.getcwd()
		if (self.os == "win32"):
			self.exec_ext=".exe"
			self.path_sep = "\\"
			#self.shell = False
			
		self.gnuplot_path = utils.which("pgnuplot" + self.exec_ext)			
	
	def _genParser(self):
		"""
		Generates an argumentparser
		
		@type	self: Options
		@param 	self: Options object
		
		@rtype:		ArgumentParser
		@return:	Parser
		"""
		parser = argparse.ArgumentParser(description='SVM Tool')
		parser.add_argument("action", 
			nargs=1, metavar="ACTION", choices=["crossValidation","train","test","merge","gui","subset"], 
			help="%(choices)s")
		parser.add_argument("-l", "--libsvm-path",
			nargs=1, metavar="PATH", default=None, 
			help="Path to libSVM")
		parser.add_argument("-p","--gnuplot-path", 
			nargs=1, metavar="PATH", default=[""], 
			help="Path to gnuplot binaries")
		parser.add_argument("-s", "--subset-size", type=int,
			nargs=1, metavar="SIZE", default=[0], 
			help="Minimal size for the subsets")
		parser.add_argument("-dd", "--division-depth", type=int,
			nargs=1, metavar="DEPTH", default=[0], 
			help="Maximal division depth")
		parser.add_argument("-df", "--division-factor", type=int, 
			nargs=1, metavar="FACTOR", default=[2], 
			help="Factor for subdivision")
		parser.add_argument("-f", "--fold", type=int, 
			nargs=1, metavar="FOLD", default=[5], 
			help="n-fold cross validation mode")
		parser.add_argument("-w", "--worker", type=int, 
			nargs=1, metavar="WORKER", default=[1],
			help="n-fold cross validation mode")
		parser.add_argument("-cr", "--c-range", type=float,
			nargs=3, metavar=("START","STOP","STEP"), default=None, 
			help="Range for C values")
		parser.add_argument("-gr", "--g-range", type=float,
			nargs=3, metavar=("START","STOP","STEP"), default=None, 
			help="Range for gamma values")
		parser.add_argument("-c", "--c-value", type=float,
			nargs=1, metavar="VALUE", default=None, 
			help="The value for C")
		parser.add_argument("-g", "--g-value", type=float,
			nargs=1, metavar="VALUE", default=None, 
			help="The value for gamma")
		parser.add_argument("-i", "--training-file", 
			nargs='+', metavar="FILE", default=None, 
			help="Path to file with training data")
		parser.add_argument("-t", "--test-file", 
			nargs='+', metavar="FILE", default=None, 
			help="Path to file with test data")
		parser.add_argument("-m", "--model-file", 
			nargs=1, metavar="FILE", default=None, 
			help="Output/input model file")
		parser.add_argument("-o", "--output-file", 
			nargs=1, metavar="FILE", default=None, 
			help="General output file")
		parser.add_argument("-aa", "--additional_arguments", 
			nargs=1, metavar="STRING", default=[""], 
			help="Additional arguments for, svm_train; svm_predict; svm_scale")
		return parser
		
	def _fullPath(self, path):
		if (self.os == "win32"):
			path = path.replace("/","\\");
			if (not path.startswith(":",1)):
				p = self.cwd + self.path_sep + path
				return p
		if (path.startswith(".")):
				return self.cwd + self.path_sep + path[1:]
				
	def process(self,argv=None):
		"""
		Process commandline Arguments
		
		
		@type	self: Options
		@param 	self: Options object
		
		@type	argv: String[]
		@param	argv: Array with arguments
		"""
		args = self._genParser().parse_args(argv)
		
		self.action = args.action[0]
		self.additional_arguments = args.additional_arguments[0]
		
		if (self._actionRequiresOption(self.action, "libsvmpath")):
			if (args.libsvm_path != None and os.path.exists(args.libsvm_path[0])):
				self.libsvm_path = args.libsvm_path[0]
			else:
				if (os.path.exists("."+self.path_sep+"libsvm")):
					self.libsvm_path = "."+self.path_sep+"libsvm"
				elif (os.path.exists("."+self.path_sep+"libs"+self.path_sep+"libsvm")):
					self.libsvm_path = "."+self.path_sep+"libs"+self.path_sep+"libsvm"
				else:
					self.libsvm_path = utils.readPath("libSVM")
			self.libsvm_path = self._fullPath(self.libsvm_path)
			
			if (self.os == "win32"):
				self.svm_scale_path = utils.findExe(self.libsvm_path + self.path_sep+"windows","svm-scale.exe", self.path_sep)
				self.svm_train_path = utils.findExe(self.libsvm_path + self.path_sep+"windows","svm-train.exe", self.path_sep )
				self.svm_predict_path = utils.findExe(self.libsvm_path + self.path_sep+"windows","svm-predict.exe", self.path_sep)
			else :
				self.svm_scale_path = utils.findExe(self.libsvm_path,"svm-scale")
				self.svm_train_path = utils.findExe(self.libsvm_path,"svm-train")
				self.svm_predict_path = utils.findExe(self.libsvm_path,"svm-predict")
			
			self.subset_py = self.libsvm_path + self.path_sep+"tools"+self.path_sep+"subset.py"
			
		if (self.gnuplot_path == None):
			self.gnuplot_path = args.gnuplot_path[0]
			if (self._actionRequiresOption(self.action,"gnuplotpath")):
				if (self.gnuplot_path == None):
					self.gnuplot_path = utils.readFilePath("pgnuplot")
					
					
		if (args.subset_size != None):
			self.subset_size = args.subset_size[0]
		elif (self._actionRequiresOption(self.action,"subsetsize")):
			self.subset_size = raw_input("Subset size:")
			
		if (args.division_depth != None):
			self.division_depth = args.division_depth[0]
			
		if (args.division_factor != None):
			self.division_factor = args.division_factor[0]
					
		self.fold = args.fold[0]
		self.worker = args.worker[0]
			
		if (self._actionRequiresOption(self.action,"crange")):
			if (args.c_range == None):
				c_range_start = raw_input("Start value for C: ")
				c_range_stop = raw_input("Stop value for C: ")
				c_range_step = raw_input("Step value for C: ")
				self.c_range = (c_range_start, c_range_stop, c_range_step)
				self.c_range_max = (c_range_start, c_range_stop, c_range_step)
			else:
				self.c_range = (args.c_range[0], args.c_range[1], args.c_range[2])
				self.c_range_max = (args.c_range[0], args.c_range[1], args.c_range[2])
				
		if (self._actionRequiresOption(self.action,"grange")):
			if(args.g_range == None):
				g_range_start = raw_input("Start value for gamma: ")
				g_range_stop = raw_input("Stop value for gamma: ")
				g_range_step = raw_input("Step value for gamma: ")
				self.g_range = (g_range_start, g_range_stop, g_range_step)
				self.g_range_max = (g_range_start, g_range_stop, g_range_step)
			else:
				self.g_range = (args.g_range[0],args.g_range[1], args.g_range[2])
				self.g_range_max = (args.g_range[0],args.g_range[1], args.g_range[2])
				
		if (self._actionRequiresOption(self.action,"trainingilfe") and ((args.training_file == None) or (not os.path.exists(args.training_file[0])))):
			self.training_file = self._fullPath(utils.readFilePath("Training-file"))
		elif (args.training_file != None):
			self.training_file = self._fullPath(args.training_file[0])
			
		if (self._actionRequiresOption(self.action,"testfile") and ((args.test_file == None) or (not os.path.exists(args.test_file[0])))):
			self.test_file = self._fullPath(utils.readFilePath("test-file"))
		elif (args.test_file != None):
			self.test_file = self._fullPath(args.test_file[0])
			
		if (self._actionRequiresOption(self.action,"modelfile") and ((args.model_file == None))):
			self.model_file = self._fullPath(utils.readFilePath("model-file"))
		elif (args.model_file != None):
			self.model_file = self._fullPath(args.model_file[0])
				
		if (self._actionRequiresOption(self.action,"cvalue") and (args.c_value == None)):
			self.c_value = raw_input("Value for C: ")
		elif (args.c_value != None):
			self.c_value = args.c_value[0]
			
		if (self._actionRequiresOption(self.action,"gvalue") and (args.g_value == None)):
			self.g_value = raw_input("Value for gamma: ")
		elif (args.g_value != None):
			self.g_value = args.g_value[0]
			
		if (args.output_file != None):
			self.output_file = self._fullPath(args.output_file[0])
		elif (self.action == "test" and self.test_file != None):
			self.output_file = self._fullPath(self.test_file + ".out")
		elif(self.training_file != None):
			self.output_file = self._fullPath(self.training_file + ".out")
		elif(self._actionRequiresOption(self.action,"outputfile")):
			self.output_file = self._fullPath(utils.readFilePath("output-file"))
				
		if (self.action == "merge"):
			self.training_file = args.training_file
			self.test_file = args.test_file
			self.output_file = args.output_file[0]
			
			
			
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
# Purpose:
# Speed up the SVM cross validation process by subdiving the input set into 
# smaller subsets with individual subset-validation.
# 
# After each validation round, the subsets get merged and the calcualated values
# for C and gamma define the new search range for the next run.
#
# Hopefully this decreases the time needed for the cross validation.
#
# For an easier use of this programm, it should look for executables by itself.
#
# ---------------------------------------------------------------------------

import sys
import traceback
import crossValidator
from threading import Thread
from utils import log, mergeFiles
from subprocess import *
from Options import Options
from libSVMConnector import train, scale, subset, predict
from treeCrossValidation import crossValidate


version = "1.0.0"

class svmTool(Thread):
	"""Main class"""

	opts = None
	"""Options object"""

	def cmdLineOptions(self):
		"""read the options form the command line"""
		self.opts = Options()
		self.opts.process()
		return self
		
	def run(self):
		"""Thread.run()"""
		try:
			if (self.opts.action == "gui"):
				import svmToolGui
				svmToolGui.gui = svmToolGui.svmToolGui(self.opts)
				svmToolGui.gui.run()
			else:	
				log("SVM Tool {0}".format(version))
				log("Using libSVM: {0}".format(self.opts.libsvm_path))
				log("\tsvm-scale: {0}".format(self.opts.svm_scale_path))
				log("\tsvm-train: {0}".format(self.opts.svm_train_path))
				log("\tsvm-predict: {0}".format(self.opts.svm_predict_path))
				log("\tsubset.py: {0}".format(self.opts.subset_py))
				if (self.opts.gnuplot_path != None):
					log("Using gnuplot: {0}".format(self.opts.gnuplot_path))
				if (self.opts.training_file != None):
					log("Training file: {0}".format(self.opts.training_file))
				if (self.opts.test_file != None):
					log("Test file: {0}".format(self.opts.test_file))
				if (self.opts.model_file != None):
					log("Model file: {0}".format(self.opts.model_file))
				if (self.opts.output_file != None):
					log("Output file: {0}".format(self.opts.output_file))
				

				if (self.opts.action == "crossValidation"):
					log("Starting cross validation")
					log("C-Range (start,stop, step): {0}".format(self.opts.c_range))
					log("Gamma-Range (start,stop, step): {0}".format(self.opts.g_range))
					log("Division depth: {0}".format(self.opts.division_depth))
					log("Division factor: {0}".format(self.opts.division_factor))
					log("Minimum subset size: {0}".format(self.opts.subset_size))
					log("Worker count: {0}".format(self.opts.worker))
					if (self.opts.additional_arguments != None and self.opts.additional_arguments != ""):
						log("Additional arguements: {0}".format(self.opts.additional_arguments))
					crossValidate(self.opts)
				elif (self.opts.action == "train"):
					log("Trainig SVM")
					log("C value: {0}".format(self.opts.c_value))
					log("Gamma value: {0}".format(self.opts.g_value))
					if (self.opts.additional_arguments != ""):
						log("Additional arguements: {0}".format(self.opts.additional_arguments))
					train(self.opts)
				elif (self.opts.action == "test"):
					log("Testing SVM")
					if (self.opts.additional_arguments != ""):
						log("Additional arguements: {0}".format(self.opts.additional_arguments))
					predict(self.opts)
				elif (self.opts.action == "merge"):
					log("Merging files")
					mergeFiles(self.opts.training_file, self.opts.output_file+".data")
					mergeFiles(self.opts.test_file, self.opts.output_file+".test")
				elif (self.opts.action == "subset"):
					log("Generating subset")
					log("Subset size: {}".format(self.opts.subset_size))
					subset(self.opts, self.opts.subset_size, self.opts.training_file, \
						self.opts.output_file+".subset_"+str(self.opts.subset_size), \
						self.opts.output_file+".restset");
				log("All done")
			
		except Exception as e:
			log("An exception occured:")
			log("\t" + e.message)
			log("Here's the stack:\n")
			(t,v,s) = sys.exc_info()
			traceback.print_tb(s)
		
		return self
		
if __name__ == "__main__":
	tool = svmTool()
	tool.cmdLineOptions()
	tool.start()
	
	exit(0)
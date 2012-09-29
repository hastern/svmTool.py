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
# Utility functions:
#	Path and file system utilities
#	Simple logging function
#
# ---------------------------------------------------------------------------


import os
import time
import sys


logListener = None
logFile = None

def setLogListener(listener):
	"""
	Adds a listener callback for the log function
	
	@type	listener: Callback
	@param	listener: callback function
	"""
	global logListener
	logListener = listener

def log(str):
	"""
	Writes a log message
	
	@type	str: String
	@param	str: Log message
	"""
	global logListener
	global logFile
	if (logFile == None):
		logFile = open("log.txt", "w", 0)
	msg = "[{0}] {1}".format(time.strftime("%H:%M:%S") , str.strip("\r\n") )
	logFile.write(msg+"\n")
	if (logListener != None):
		logListener(msg+"\n")
	print msg
	sys.stdout.flush()
	

def is_exe(fpath):
	"""
	Tests if a file is an executable
	
	@type	fpath: String
	@param 	fpath: filename/-path
	
	@rtype:		boolean
	@return:	True, if the file is an executable
	"""
	return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
	
def findExe(path,exe,sep="/"):
	"""
	Test if an executable exists in a path
	
	@type	path: String
	@param	path: Source path
	
	@type	exe: String
	@param	exe: Name of the executable
	
	@rtype:		String
	@return: 	complete filepath
	
	@raise	Exception: If file is not found
	"""
	f = path + sep + exe
	if (os.path.exists(path)):
		if (is_exe(f)):
			return f
	raise Exception("Executable {} not found!".format(exe))
	
def which(program):
	"""
	Looks for a programm in system environment path
	
	@type	program: String
	@param	program: Program name
	
	@rtype:		String
	@return:	Path to program or None
	"""
	fpath, fname = os.path.split(program)
	print fpath
	if fpath:
		if is_exe(program):
			return program
	else:
		for path in os.getenv("PATH").split(os.pathsep):
			exe_file = os.path.join(path, program)
			if is_exe(exe_file):
				return exe_file
	return None    

def readPath(target):
	"""
	Reads a path from standard input.
	This will be repeated until the given path is valid.
	
	@type	target: String
	@param	target: Name for the path
	
	@rtype:		String
	@return:	path to target
	"""
	while True:
		p = raw_input(target + " Path: ")
		if (os.path.exists(p)):
			break
		print("ERROR: Path '{0}' doesn't exist!".format(p))
	return p

def readFilePath(target):
	"""
	Reads a path to a file form standard input.
	This will be repeated until a valid and existing file is given.
	
	@type	target: String
	@param	target: Name of the file or a descriptive name
	
	@rtype:		String
	@return:	path to targetfile
	"""
	while True:
		f = raw_input("Path to '" + target + "': ")
		if (os.path.exists(f) and os.path.isfile(f)):
			break
		print("ERROR: File '{0}' doesn't existis!".format(f))
	return f
	
def mergeFiles(files,outfile):
	"""
	Merging multiple files into one.
	
	@type	files: Array
	@param	files: Array with fileanmes
	
	@type	outfile: String
	@param	outfile: Name of the output file
	"""
	if (files == None):
		return 0
	else:
		out = open(outfile,"w")
		for file in files:
			f = open(file,"r")
			for line in f.readlines():
				out.write(line)
			f.close()
		out.close()
	
	
	
	
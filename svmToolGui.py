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
# Graphical User Interface
#
# ---------------------------------------------------------------------------

import os
import Tkinter as guitk
import tkFileDialog as fileDiag
import utils
from Options import Options

gui = None
"""Global GUI handle"""
		
class svmToolGui:
	"""Graphical User Interface for the svmTool"""
	
	radioAction = "crossValidation"
	"""Variable holding the action, selected via radiobutton"""
	mainW = None
	"""Main window handle"""
	opts = None
	"""Object object"""
	
	@staticmethod
	def setEditValue(edt, value):
		"""
		sets the value of an entry field
		
		@type	edt: Tkinter.Entry
		@param	edt: Text field
		
		@type	value: String
		@param 	value: Text for the text field
		"""
		global gui
		edt.delete(0, guitk.END)
		edt.insert(guitk.INSERT, value)

	@staticmethod
	def handleFileOpen(edt):
		"""
		Open file dialog from TK Interface
		
		@type	edt: Tkinter.Entry
		@param	edt: Textfield for result
		"""
		global gui
		fn = fileDiag.askopenfilename(initialdir=".")
		svmToolGui.setEditValue(edt, fn)

	@staticmethod
	def trainfile():
		"""Eventhandler for training file select button click"""
		global gui
		svmToolGui.handleFileOpen(gui.trainFile)
		

	@staticmethod
	def testfile():
		"""Eventhandler for test file select button click"""
		global gui
		svmToolGui.handleFileOpen(gui.testFile)
		

	@staticmethod
	def modelfile():
		"""Eventhandler for model file select button click"""
		global gui
		svmToolGui.handleFileOpen(gui.modelFile)
			
	@staticmethod
	def outputfile():
		"""Eventhandler for output file select button click"""
		global gui
		svmToolGui.handleFileOpen(gui.outputFile)
		
	@staticmethod
	def libsvmpath():
		"""Eventhandler for libsvm path select button click"""
		global gui
		dir = fileDiag.askdirectory(initialdir=".")
		svmToolGui.setEditValue(gui.libSVMPath, dir)
		if (gui.opts.os == "win32"):
			svmToolGui.setEditValue(gui.libSVMScale, utils.findExe(dir + gui.opts.path_sep+"windows","svm-scale.exe", gui.opts.path_sep))
			svmToolGui.setEditValue(gui.libSVMTrain, utils.findExe(dir + gui.opts.path_sep+"windows","svm-train.exe", gui.opts.path_sep))
			svmToolGui.setEditValue(gui.libSVMPredict, utils.findExe(dir + gui.opts.path_sep+"windows","svm-predict.exe", gui.opts.path_sep))
		else :
			svmToolGui.setEditValue(gui.libSVMScale, utils.findExe(dir,"svm-scale"))
			svmToolGui.setEditValue(gui.libSVMTrain, utils.findExe(dir,"svm-train"))
			svmToolGui.setEditValue(gui.libSVMPredict, utils.findExe(dir,"svm-predict"))
		if (os.path.isfile(dir+gui.opts.path_sep+"tools"+gui.opts.path_sep+"subset.py")):
			svmToolGui.setEditValue(gui.subset_pyPath, dir+gui.opts.path_sep+"tools"+gui.opts.path_sep+"subset.py")

	@staticmethod
	def guiLogListener(msg):
		"""Callback function for log listener"""
		global gui
		if (gui != None):
			gui.logText.insert(guitk.END, msg)
			gui.mainW.update()
			
	@staticmethod
	def clear():
		"""Eventhandler for clear button click"""
		global gui
		if (gui != None):
			gui.logText.delete(1.0, guitk.END)
			
	
	@staticmethod
	def preparePath(path):
		"""Prepare the path based on the operation system"""
		global gui
		if (gui.opts.os == "win32"):
			return path.replace("\\","\\\\").replace("/","\\\\")
		else:
			return path
			
	@staticmethod
	def getPathValue(hnd):
		"""Gets the value from an input field"""
		return svmToolGui.preparePath(hnd.get())
			
	@staticmethod
	def start():
		"""Eventhandler for start button click"""
		global gui
		from svmTool import svmTool
		gui.opts.action = gui.radioAction
		gui.opts.training_file = svmToolGui.getPathValue(gui.trainFile)
		gui.opts.test_file = svmToolGui.getPathValue(gui.testFile)
		gui.opts.model_file = svmToolGui.getPathValue(gui.modelFile)
		gui.opts.output_file = svmToolGui.getPathValue(gui.outputFile)
		gui.opts.libsvm_path = svmToolGui.getPathValue(gui.libSVMPath)
		gui.opts.svm_scale_path = svmToolGui.getPathValue(gui.libSVMScale)
		gui.opts.svm_train_path = svmToolGui.getPathValue(gui.libSVMTrain)
		gui.opts.svm_predict_path = svmToolGui.getPathValue(gui.libSVMPredict)
		gui.opts.subset_py = svmToolGui.getPathValue(gui.subset_pyPath)
		gui.opts.gnuplot_path = svmToolGui.getPathValue(gui.gnuplotPath)
		gui.opts.c_range = int(gui.cstart.get()),int(gui.cstop.get()),int(gui.cstep.get())
		gui.opts.c_range_max = gui.opts.c_range
		gui.opts.g_range = int(gui.gstart.get()),int(gui.gstop.get()),int(gui.gstep.get())
		gui.opts.g_range_max = gui.opts.g_range
		gui.opts.subset_size = int(gui.subsetSize.get())
		gui.opts.division_depth = int(gui.depth.get())
		gui.opts.division_factor = int(gui.factor.get())
		gui.opts.fold = int(gui.fold.get())
		gui.opts.worker = int(gui.worker.get())
		
		if (gui.opts.os == "win32"):
			gui.opts.shell = False
		
		tool = svmTool()
		tool.opts = gui.opts
		tool.start()
		

		
	def _genSpinBox(self, master, min, max, value):
		"""
		Create a spinbox
		
		@type	master: Tkinter.Widget
		@param	master: Parent widget
		
		@type	min: Int
		@param	min: Minimum value
		
		@type	max: Int
		@param	max: Maximum value
		
		@type	value: Int
		@param	value: Default value
		"""
		hnd = guitk.Spinbox(master, from_=min, to=max, width=5)
		hnd.delete(0, guitk.END)
		hnd.insert(guitk.INSERT, value)
		return hnd	

	def _labelInput(self,master, lbl, min=0, max=100, val=0):
		"""
		Create an labeld input
		
		@type	master: Tkinter.Widget
		@param	master: Parent widget
		
		@type	lbl: String
		@param	lbl: Label text
		
		@type	min: Int
		@param	min: Minimum Value
		
		@type	max: Int
		@param	max: Maximum Value
		
		@type	val: Int
		@param	val: Default value
		"""
		f = guitk.Frame(master, padx=5)
		guitk.Label(f, text=lbl, width=20, anchor=guitk.W).pack(side=guitk.LEFT)
		sb = self._genSpinBox(f, min, max, val)
		sb.pack(side=guitk.LEFT)
		f.pack()
		return sb
	
	def _getFile(self, master, lbl, var=None, cmd=None):
		"""
		Generate a file selection 
		
		@type	master: Tkinter.Widget
		@param	master: Parent widget
		
		@type	lbl: String
		@param	lbl: Label text
		
		@type	var: String
		@param	var: Default Text
		
		@type	cmd: Callback
		@param	cmd: Callback function
		"""
		f = guitk.Frame(master, padx=5)
		guitk.Label(f, text=lbl, width=15, anchor=guitk.W).pack(side=guitk.LEFT)
		edt = guitk.Entry(f, width=40)
		edt.pack(side=guitk.LEFT)
		guitk.Button(f, text="...", command=cmd).pack(side=guitk.LEFT)
		f.pack()
		if (var != None):
			edt.delete(0,guitk.END)
			edt.insert(guitk.INSERT,var)
		return edt

	def __init__(self, options = Options()):
		"""
		Constructor
		
		@type	options: Options
		@param	options: Options object
		"""
		self.opts = options
	
		self.mainW = guitk.Tk()
		
		utils.setLogListener(svmToolGui.guiLogListener)
		
		cfgFrame = guitk.Frame(self.mainW, padx=5, pady=5)
		
		self.trainFile = self._getFile(cfgFrame, "Training File", self.opts.training_file, svmToolGui.trainfile)
		self.testFile = self._getFile(cfgFrame, "Test File", self.opts.test_file, svmToolGui.testfile)
		self.modelFile = self._getFile(cfgFrame, "Model File", self.opts.model_file, svmToolGui.modelfile)
		self.outputFile = self._getFile(cfgFrame, "Output File", self.opts.output_file, svmToolGui.outputfile)
		self.libSVMPath = self._getFile(cfgFrame, "libSVM Path", self.opts.libsvm_path, svmToolGui.libsvmpath)
		self.libSVMScale = self._getFile(cfgFrame, "SVM Scale Path", self.opts.svm_scale_path)
		self.libSVMTrain = self._getFile(cfgFrame, "SVM Train Path", self.opts.svm_train_path)
		self.libSVMPredict = self._getFile(cfgFrame, "SVM Predict Path", self.opts.svm_predict_path)
		self.subset_pyPath = self._getFile(cfgFrame, "subset.py Path", self.opts.subset_py)
		self.gnuplotPath = self._getFile(cfgFrame, "gnuplot Path", self.opts.gnuplot_path)
		
		rangeFrame = guitk.Frame(cfgFrame, padx=5, pady=5)
		guitk.Label(rangeFrame, text="Start").grid(row=0,column=1)
		guitk.Label(rangeFrame, text="Stop").grid(row=0,column=2)
		guitk.Label(rangeFrame, text="Step").grid(row=0,column=3)
		guitk.Label(rangeFrame, text="C Range").grid(row=1,column=0, sticky=guitk.W)
		guitk.Label(rangeFrame, text="Gamma Range").grid(row=2,column=0, sticky=guitk.W)
		self.cstart = self._genSpinBox(rangeFrame, -99, 99, -3)
		self.cstart.grid(row=1,column=1)
		self.cstop = self._genSpinBox(rangeFrame, -99, 99, 15)
		self.cstop.grid(row=1,column=2)
		self.cstep = self._genSpinBox(rangeFrame, -99, 99, 2)
		self.cstep.grid(row=1,column=3)
		self.gstart = self._genSpinBox(rangeFrame, -99, 99, 3)
		self.gstart.grid(row=2,column=1)
		self.gstop = self._genSpinBox(rangeFrame, -99, 99, -15)
		self.gstop.grid(row=2,column=2)
		self.gstep = self._genSpinBox(rangeFrame, -99, 99, -2)
		self.gstep.grid(row=2,column=3)
		rangeFrame.pack()
		
		
		optsFrame = guitk.Frame(cfgFrame, padx=5, pady=5)
		self.subsetSize = self._labelInput(optsFrame, "Minimum Subset Size",min=1)
		self.depth = self._labelInput(optsFrame, "Division Depth", min=0, val=0)
		self.factor = self._labelInput(optsFrame, "Division Factor", min=1, val=1)
		self.fold = self._labelInput(optsFrame, "Fold (Cross Validation)", min=1, val=5)
		self.worker = self._labelInput(optsFrame, "Worker", min=1, val=1)
		optsFrame.pack()
		
		actionFrame = guitk.LabelFrame(cfgFrame, text="Action", padx=5, pady=5)
		guitk.Radiobutton(actionFrame, text="Cross Validation", variable=svmToolGui.radioAction, value="crossValidation").pack(side=guitk.LEFT)
		guitk.Radiobutton(actionFrame, text="Train Model", variable=svmToolGui.radioAction, value="train").pack(side=guitk.LEFT)
		guitk.Radiobutton(actionFrame, text="Test Model", variable=svmToolGui.radioAction, value="test").pack(side=guitk.LEFT)
		actionFrame.pack()
		
		guitk.Button(cfgFrame, text="Start", command=svmToolGui.start).pack(side=guitk.RIGHT)
		guitk.Button(cfgFrame, text="Clear", command=svmToolGui.clear).pack(side=guitk.RIGHT)
		cfgFrame.pack(side=guitk.LEFT)
		
		scroll = guitk.Scrollbar(self.mainW)
		scroll.pack(side=guitk.RIGHT, fill=guitk.Y)
		
		self.logText = guitk.Text(self.mainW)
		self.logText.pack(side=guitk.LEFT, fill=guitk.BOTH, expand=1)
		self.logText.config(yscrollcommand=scroll.set)
		scroll.config(command=self.logText.yview)

	def run(self):
		self.mainW.mainloop()


		
if __name__ == "__main__":
	gui = svmToolGui()
	gui.run()
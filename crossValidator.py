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
# grid.py fork without main function
# 
# ---------------------------------------------------------------------------

import os, sys, traceback
import getpass
import Options
from utils import log
from threading import Thread
from subprocess import *
from libSVMConnector import *

if(sys.hexversion < 0x03000000):
	import Queue
else:
	import queue as Queue


global pass_through_string


def start_gnuplot(exe):
	return Popen(exe,stdin = PIPE).stdin

def range_f(begin,end,step):
	# like range, but works on non-integer too
	seq = []
	while True:
		if step > 0 and begin > end: break
		if step < 0 and begin < end: break
		seq.append(begin)
		begin = begin + step
	return seq

def permute_sequence(seq):
	n = len(seq)
	if n <= 1: return seq

	mid = int(n/2)
	left = permute_sequence(seq[:mid])
	right = permute_sequence(seq[mid+1:])

	ret = [seq[mid]]
	while left or right:
		if left: ret.append(left.pop(0))
		if right: ret.append(right.pop(0))

	return ret

def redraw(opts,gnuplot,datafile,db,best_param,tofile=False):
	if len(db) == 0: return
	begin_level = round(max(x[2] for x in db)) - 3
	step_size = 0.5
	
	c_begin, c_end, c_step = opts.c_range
	g_begin, g_end, g_step = opts.g_range
	best_log2c,best_log2g,best_rate = best_param

	# if newly obtained c, g, or cv values are the same,
	# then stop redrawing the contour.
	if all(x[0] == db[0][0]  for x in db): return
	if all(x[1] == db[0][1]  for x in db): return
	if all(x[2] == db[0][2]  for x in db): return

	if tofile:
		gnuplot.write(b"set term png transparent small linewidth 2 medium enhanced\n")
		gnuplot.write("set output \"{0}\"\n".format((datafile+".png").replace('\\','\\\\')).encode())
		#gnuplot.write(b"set term postscript color solid\n")
		#gnuplot.write("set output \"{0}.ps\"\n".format(dataset_title).encode().encode())
	elif is_win32:
		gnuplot.write(b"set term windows\n")
	else:
		gnuplot.write( b"set term x11\n")
	
	gnuplot.write(b"set xlabel \"log2(C)\"\n")
	gnuplot.write(b"set ylabel \"log2(gamma)\"\n")
	gnuplot.write("set xrange [{0}:{1}]\n".format(c_begin,c_end).encode())
	gnuplot.write("set yrange [{0}:{1}]\n".format(g_begin,g_end).encode())
	gnuplot.write(b"set contour\n")
	gnuplot.write("set cntrparam levels incremental {0},{1},100\n".format(begin_level,step_size).encode())
	gnuplot.write(b"unset surface\n")
	gnuplot.write(b"unset ztics\n")
	gnuplot.write(b"set view 0,0\n")
	#gnuplot.write("set title \"{0}\"\n".format(dataset_title).encode())
	gnuplot.write(b"unset label\n")
	gnuplot.write("set label \"Best log2(C) = {0}  log2(gamma) = {1}  accuracy = {2}%\" \
				at screen 0.5,0.85 center\n". \
				format(best_log2c, best_log2g, best_rate).encode())
	gnuplot.write("set label \"C = {0}  gamma = {1}\""
					" at screen 0.5,0.8 center\n".format(2**best_log2c, 2**best_log2g).encode())
	gnuplot.write(b"set key at screen 0.9,0.9\n")
	gnuplot.write(b"splot \"-\" with lines\n")
	


	
	db.sort(key = lambda x:(x[0], -x[1]))

	prevc = db[0][0]
	for line in db:
		if prevc != line[0]:
			gnuplot.write(b"\n")
			prevc = line[0]
		gnuplot.write("{0[0]} {0[1]} {0[2]}\n".format(line).encode())
	gnuplot.write(b"e\n")
	gnuplot.write(b"\n") # force gnuplot back to prompt when term set failure
	gnuplot.flush()


def calculate_jobs(opts):
	c_begin, c_end, c_step = opts.c_range
	g_begin, g_end, g_step = opts.g_range
	c_seq = permute_sequence(range_f(c_begin,c_end,c_step))
	g_seq = permute_sequence(range_f(g_begin,g_end,g_step))
	nr_c = float(len(c_seq))
	nr_g = float(len(g_seq))
	i = 0
	j = 0
	jobs = []

	while i < nr_c or j < nr_g:
		if i/nr_c < j/nr_g:
			# increase C resolution
			line = []
			for k in range(0,j):
				line.append((c_seq[i],g_seq[k]))
			i = i + 1
			jobs.append(line)
		else:
			# increase g resolution
			line = []
			for k in range(0,i):
				line.append((c_seq[k],g_seq[j]))
			j = j + 1
			jobs.append(line)
	return jobs

class WorkerStopToken:  # used to notify the worker to stop
		pass

class Worker(Thread):
	def __init__(self,name,job_queue,result_queue,opts,datafile):
		Thread.__init__(self)
		self.name = name
		self.job_queue = job_queue
		self.result_queue = result_queue
		self.opts = opts
		self.datafile = datafile
	def run(self):
		while True:
			(cexp,gexp) = self.job_queue.get()
			if cexp is WorkerStopToken:
				self.job_queue.put((cexp,gexp))
				#log('worker {0} stop.'.format(self.name))
				break
			try:
				rate = self.run_one(2.0**cexp,2.0**gexp,self.opts,self.datafile)
				if rate is None: raise RuntimeError("get no rate")
			except:
				# we failed, let others do that and we just quit
			
				#traceback.print_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
				
				self.job_queue.put((cexp,gexp))
				log('worker {0} quit.'.format(self.name))
				break
			else:
				self.result_queue.put((self.name,cexp,gexp,rate))

class LocalWorker(Worker):
	def run_one(self,c,g,opts,datafile):
		#cmdline = '"{0}" -c {1} -g {2} -v {3} "{4}"'.format \
		#  (opts.svm_train_path,c,g,opts.fold,datafile)
		#result = Popen(cmdline,shell=opts.shell,stdout=PIPE).stdout
		result = train(opts,c,g,datafile)
		for line in result.readlines():
			if str(line).find("Cross") != -1:
				#log("SVM Train: {}".format(line))
				return float(line.split()[-1][0:-1])

def validate(opts,datafile):

	# put jobs in queue

	jobs = calculate_jobs(opts)
	job_queue = Queue.Queue(0)
	result_queue = Queue.Queue(0)

	for line in jobs:
		for (c,g) in line:
			job_queue.put((c,g))

	# hack the queue to become a stack --
	# this is important when some thread
	# failed and re-put a job. It we still
	# use FIFO, the job will be put
	# into the end of the queue, and the graph
	# will only be updated in the end
 
	job_queue._put = job_queue.queue.appendleft
	
	# fire local workers

	for i in range(opts.worker):
		LocalWorker('local',job_queue,result_queue,opts,datafile).start()
		
	# Start Gnuplot
	
	#gp = start_gnuplot(opts.gnuplot_path)

	# gather results

	done_jobs = {}


	result_file = open(opts.output_file, 'w')


	db = []
	best_rate = -1
	best_c,best_g = 0,0
	best_c1,best_g1 = None,None

	for line in jobs:
		for (c,g) in line:
			while (c, g) not in done_jobs:
				(worker,c1,g1,rate) = result_queue.get()
				done_jobs[(c1,g1)] = rate
				result_file.write('{0} {1} {2}\n'.format(c1,g1,rate))
				result_file.flush()
				if (rate > best_rate) or (rate==best_rate and g1==best_g1 and c1<best_c1):
					best_rate = rate
					best_c1,best_g1=c1,g1
					best_c = c1
					best_g = g1
				#print("[{0}] {1} {2} {3} (best c={4}, g={5}, rate={6})".format(worker,c1,g1,rate,best_c, best_g, best_rate))
			db.append((c,g,done_jobs[(c,g)]))
		#redraw(opts,gp,db,[best_c1, best_g1, best_rate])
		#redraw(opts,gp,db,[best_c1, best_g1, best_rate],True)

	job_queue.put((WorkerStopToken,None))
	#print("{0} {1} {2}".format(best_c, best_g, best_rate))
	return best_c, best_g, best_rate

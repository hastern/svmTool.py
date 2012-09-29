svmTool.py
==========

svmTool.py is an interface program to be used with [libSVM](http://www.csie.ntu.edu.tw/~cjlin/libsvm/).

Mainly it integrates the tools svm-scale, svm-train, svm-predict into one single application.
Since the usage of the python-scripts bundled with libSVM is (in my opinion) pretty annoying, 
I integrated most of their functionality by either forking or calling them.

For further usage information consult the internal help of the tool. (svmTool.py --help)

In order to get this up an running you additionally need to download the [libSVM](http://www.csie.ntu.edu.tw/~cjlin/libsvm/) 
and also get some data for training your SVM.






This project started at the [University of Applied Science, Wedel (Germany)](http://fh-wedel.de) as a part of the lecture
"*Learning & Softcomputing*".
ps -ef |grep python |awk '{print $2}'|xargs kill -9
ps -ef |grep phantomjs |awk '{print $2}'|xargs kill -9
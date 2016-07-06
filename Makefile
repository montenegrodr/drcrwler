build:
	#wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
	bzip2 -d phantomjs-2.1.1-linux-x86_64.tar.bz2
	tar -xf phantomjs-2.1.1-linux-x86_64.tar
	mv phantomjs-2.1.1-linux-x86_64 phantomjs1
	tar -xf phantomjs-2.1.1-linux-x86_64.tar
	mv phantomjs-2.1.1-linux-x86_64 phantomjs2
	rm phantomjs-2.1.1-linux-x86_64.tar
	sudo apt-get install libmysqlclient-dev
	pip install -r requirements.txt



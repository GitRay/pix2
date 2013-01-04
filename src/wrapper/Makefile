# $Id$

# DO NOT SET ANY OF THESE TO 'root'!
HTTPD_USER = www-data
QUICKYPIX_UNAME = photo-data
QUICKYPIX_GNAME = photo-data
QUICKYPIX_CMD = /home/quarl/proj/quickypix/src/quickypix/quickypix.cgi

quickypix.cgi.su: quickypix.cgi.su.c quickypix.cgi.su.h
	cc -Wall -o quickypix.cgi.su quickypix.cgi.su.c -D'HTTPD_USER="$(HTTPD_USER)"'  -D'QUICKYPIX_UNAME="$(QUICKYPIX_UNAME)"' -D'QUICKYPIX_GNAME="$(QUICKYPIX_GNAME)"' -D'QUICKYPIX_CMD="$(QUICKYPIX_CMD)"'
	sudo chown $(QUICKYPIX_UNAME):$(QUICKYPIX_GNAME) quickypix.cgi.su
	sudo chmod ug+sx quickypix.cgi.su


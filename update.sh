#!/bin/sh

git pull update master

if [ -d "public" ]; then
	rm -rf resources/
	mv -f public/* .
	rm -rf public/
	echo "Update done"
else
	echo "No update needed"
fi

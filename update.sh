#!/bin/sh

git pull update master

rm -rf resources/
mv public/* .
rm -rf public

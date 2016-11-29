#!/bin/bash

#set -ex

echo "Launch the tests!!!"

shared="1 15 24 36 45"

while [ $# -gt 0 ]
do
	case "$1" in
		-0)
			shift
			if [ $# -gt 0 ]
			then
				export AGENT0=$1
			else
				echo "No agent specified"
				exit 1
			fi
			shift
			;;
		-1)
			shift
			if [ $# -gt 0 ]
			then
				export AGENT1=$1
			else
				echo "No agent specified"
				exit 1
			fi
			shift
			;;
		*)
			break
			;;
	esac
done


for i in {1..10}
do
	export seed=$RANDOM
	echo "$AGENT0 VS. $AGENT1 -- Seed: $seed"
	python3 gui.py -ai0 $AGENT0 -ai1 $AGENT1 -s $seed -q
	echo "$AGENT1 vs. $AGENT0 -- Seed: $seed"
	python3 gui.py -ai0 $AGENT1 -ai1 $AGENT0 -s $seed -q
done

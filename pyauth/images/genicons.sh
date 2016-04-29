#!/bin/bash
# Generate sized icon images from 512x512 masters

for n in PyAuth PyAuth-white PyAuth-grey PyAuth-dark
do
    for s in 16 24 32 48 64 128 256
    do
        convert ${n}.png -scale ${s}x${s} ${s}x${s}/${n}.png
    done
done

exit 0

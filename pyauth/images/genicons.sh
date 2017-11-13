#!/bin/bash
# Generate sized icon images from 512x512 masters

for s in 16 24 32 48 64 128 256
do
    [ -d ${s}x${s} ] || mkdir ${s}x${s}
done

for n in PyAuth PyAuth-white PyAuth-grey PyAuth-dark
do
    for s in 16 24 32 48 64 128 256
    do
        convert ${n}.png -scale ${s}x${s} ${s}x${s}/${n}.png
    done

    i=`basename $n`.ico
    icotool -c --icon -o ${i} 256x256/${n} 128x128/${n} 64x64/${n} 32x32/${n} 24x24/${n} 16x16/${n}
done

exit 0

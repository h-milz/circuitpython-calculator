#!/bin/bash

# preparation: https://learn.adafruit.com/building-circuitpython/build-circuitpython

# select your desired ports - raspberrypi does not build yet. 
PORTS="atmel-samd raspberrypi espressif mimxrt10xx"
VER="9.0.x"

# we always do a fresh clone for preparation
if [ -d circuitpython ] ; then
    rm -fr circuitpython.OLD
    mv circuitpython circuitpython.OLD
fi     
git clone git@github.com:adafruit/circuitpython.git
cd circuitpython
git checkout $VER
git submodule update --init --depth=1 --  extmod/ulab
cd ports
for i in $PORTS ; do 
	cd $i 
	make fetch-port-submodules 
	cd ..
done 
cd .. 
patch -p1 < ../circuitpython-$VER.diff 

echo "
Prep finished. 

Now you can go to the desired ports directory and build the image for your board, e.g. 

cd circuitpython/ports/atmel-samd/
make -j12 BOARD=feather_m4_express V='steps commands'  clean
make -j12 BOARD=feather_m4_express V='steps commands'  

" 


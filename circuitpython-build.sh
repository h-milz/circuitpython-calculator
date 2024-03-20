#!/bin/bash

# Vorbereitung: https://learn.adafruit.com/building-circuitpython/build-circuitpython

rm -fr circuitpython.OLD
mv circuitpython circuitpython.OLD
git clone git@github.com:adafruit/circuitpython.git
cd circuitpython
git checkout 9.0.x
pushd ports/atmel-samd/
make fetch-port-submodules
popd
patch  -p1 < ../circuitpython.diff 
cd ports/atmel-samd/
make  -j12 BOARD=feather_m4_express V="steps commands"  clean
make  -j12 BOARD=feather_m4_express V="steps commands"  


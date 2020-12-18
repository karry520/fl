#!/bin/bash

#rm -rf build/*
##### skrum ######
rm Skrum_lib/SKRUM*.so
echo "rm Skrum.so!"
cd build
#make clean
cmake -DCMAKE_POSITION_INDEPENDENT_CODE=ON ..
make -j8

cp lib/SKRUM*.so ../Skrum_lib/
echo "cp SKRUM.so!"
#cd ../


##### kd #######
#rm KD_lib/KD*.so
#echo "rm KD.so!"
#cd build
##make clean
#cmake -DCMAKE_POSITION_INDEPENDENT_CODE=ON ..
#make -j8
#
#cp lib/KD*.so ../KD_lib/
#echo "cp KD.so!"
#cd ../
# python $1

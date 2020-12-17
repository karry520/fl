#!/bin/bash

rm KD_lib/KD*.so
echo "rm KD.so!"
cd build 
#make clean 
cmake -DCMAKE_POSITION_INDEPENDENT_CODE=ON ..
make -j8

cp lib/KD_lib*.so ../KD_lib/
echo "cp KD.so!"
cd ../
# python $1

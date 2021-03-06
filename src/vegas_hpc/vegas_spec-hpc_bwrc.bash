#!/bin/bash
# Set environment variables for VEGAS, bash version
echo "This script is specific to spec-hpc-xx at the BWRC"
echo "Setting VEGAS_DIR, CUDA, PYSLALIB, VEGAS_INCL/BIN/LIB, PATH, PYTHONPATH and LD_LIBRARY_PATH for VEGAS..."

# Note: user must set the VEGAS variable in their bash startup script

export VEGAS_DIR=$VEGAS/vegas_hpc

export CUDA=/opt/vegas/cuda

export PYSLALIB=/opt/vegas/lib/python2.5/site-packages/pyslalib

export VEGAS_INCL=/opt/vegas/include
export VEGAS_BIN=/opt/vegas/bin
export VEGAS_LIB=/opt/vegas/lib
export VEGAS_LIB_GCC=/usr/lib/gcc/x86_64-redhat-linux/3.4.6

export PATH=$VEGAS_DIR/bin:$CUDA/bin:$VEGAS_BIN:$PATH

export PYTHONPATH=$VEGAS/lib/python/site-packages:$VEGAS/lib/python:$VEGAS_DIR/python:/opt/vegas/lib/python2.5/site-packages:$PYTHONPATH

export LD_LIBRARY_PATH=$PYSLALIB:$VEGAS_LIB:$CUDA/lib64:$LD_LIBRARY_PATH


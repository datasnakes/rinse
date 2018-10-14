#!/bin/bash

wget https://cran.r-project.org/src/base/R-3/R-{rversion}.tar.gz
mkdir r_installation
tar -xvf R-{rversion}.tar.gz -C r_installation/
cd r_installation
cd R-{rversion}
./configure --help
./configure --prefix={prefix}
make
make install

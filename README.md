# cv4ag
Computer vision application over satellite RGB tiles for agricultural land detection

# Install
1. Make sure package manager is allowed to get all packages
2. Clone repo: ```git clone https://github.com/worldbank/cv4ag.git```
3. Install packages outlined in ```requirements/linux-deb-pkgs.txt```
4. Install python packages outlined in ```requirements/python-pkgs.txt```
5. Download tar-archive cudnn7.0 (!) from NVidia and uncompress (```tar -xvf $/PATH/TO/TARARCHIVE```)
6. Make sure all export paths are correct (see requirements/paths-to-export.txt) and ```export``` paths
7. Clone caffe-sefnet: ```git clone https://github.com/alexgkendall/caffe-segnet.git```
8. ```cd``` to ```caffe-segnet```
8.1 Copy ```cv4ag/requirements/Makefile.config``` to ```caffe-segnet/.```
8.2 ```make all;make test;make runtest; make pycaffe```

# Licence
See LICENCE.md

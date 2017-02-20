# cv4ag
Computer vision application over satellite RGB tiles for agricultural land detection
24
# Install on Linux (Ubuntu)
1. Make sure package manager is allowed to get all packages and is updated ```sudo apt update```
2. Clone repo: ```git clone https://github.com/worldbank/cv4ag.git```
3. ```sudo bash requirements/install_linux.sh```
4. Install CUDA v.7.5 (!). If necessary, uninstall previous installations  ```sudo /usr/bin/nvidia-uninstall;sudo apt-get purge cuda```, then do ```wget http://developer.download.nvidia.com/compute/cuda/7.5/Prod/local_installers/cuda-repo-ubuntu1504-7-5-local_7.5-18_amd64.deb; sudo dpkg -i cuda-repo-ubuntu1504-7-5-local_7.5-18_amd64.deb; sudo apt-get update; sudo apt-get install cuda-7.5; rm cuda-repo-ubuntu1504-7-5-local_7.5-18_amd64.deb``` and reboot device.
5. [Download tar-archive CUDNNv.3](https://developer.nvidia.com/cudnn) (only v3 works!) from NVidia and uncompress (```tar -xvf $/PATH/TO/TARARCHIVE```)
6. Make sure all export paths are correct (see ```requirements/paths-to-export.txt```),  change ```/home/ubuntu/cudnn``` to CUDNN path and ```/home/ubuntu/caffe-segnet``` to Caffe-SegNet path. Then ```export``` paths and attach to ```~/.bashrc```.
7. Create symbolic links:  ```cd /usr/lib/x86_64-linux-gnu; sudo ln -s libhdf5_serial_hl.so.10.0.2 libhdf5_hl.so;sudo ln -s libhdf5_serial.so.10.1.0 libhdf5.so;cd``` (change libhdf version if necessary)
8. Clone caffe-segnet: ```git clone https://github.com/alexgkendall/caffe-segnet.git```
9. ```cd``` to ```caffe-segnet```
10. Copy ```cv4ag/requirements/Linux_Makefile.config``` to ```caffe-segnet/Makefile.config``` and change ```/home/ubuntu/cudnn``` to CUDNN path
11. ```make all;make test;make runtest; make pycaffe```

(non-anaconda, might need to uninstall anaconda first)

# Install on Mac
Remark: No CUDNN and GPU support

1. Make sure you have installed homebrew. (If not ```/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"```
2. Clone repo: ```git clone https://github.com/worldbank/cv4ag.git```
3. ```cd``` to repo
4. ```source requirements/install_mac.sh```
5. ```brew update;brew cask update;brew install Caskroom/cask/cuda```
6. Clone caffe-sefnet: ```git clone https://github.com/alexgkendall/caffe-segnet.git```
7. ```cd``` to ```caffe-segnet```
8. ```echo "export PYTHONPATH=/PATH/TO/caffe-segnet/python:\$PYTHONPATH">>~/.bash_profile; source ~/.bash_profile``` (change ```/PATH/TO```)
9. Copy ```cv4ag/requirements/Mac_Makefile.config``` to ```caffe-segnet/Makefile.config``` and change parameters in Makefile.config, if necessary
10. ```make all;make test;make runtest; make pycaffe```

## Remarks for Anaconda Python Installation

```echo "export ANACONDA_HOME=$HOME/anaconda">>~/.bash_profile```

```echo "export DYLD_FALLBACK_LIBRARY_PATH=$ANACONDA_HOME/lib:/usr/local/lib:/usr/lib">>~/.bash_profile```

```source ~/.bash_profile```

#Usage
```
usage: cv4ag.py [-h] [-i FILE] [-s FILE] [-o PATH] [-c N] [-z N] [-x N] [-y N]
                [-d FILETYPE_CODE] [-n N] [--lonshift N.N] [--latshift N.N]
                [--shiftformat N] [--top N] [--key KEY] [--epsg N] [--layer N]
                [--mode MODE] [--arg1 ARG1] [--arg2 ARG2] [--arg3 ARG3]
                [--arg4 ARG4] [--test | --no-test]
                [--background | --no-background] [--random | --no-random]
                OPTION [MAPBOX_TOKEN]

Machine Learning Framework for Agricultural Data.

positional arguments:
  OPTION            The modules to be loaded. OPTION: all - all modules
                    (except clear). parse - input file parser. satellite - get
                    satellite data. overlay - overlay classification with
                    satellite data. train - train. ml - apply machine learning
                    algorithm. clear - clear generated data from previous run
                    on input file
  MAPBOX_TOKEN      Mapbox token to download satellite images .

optional arguments:
  -h, --help        show this help message and exit
  -i FILE           Input file. Do not give if data obtained by script.
  -s FILE           Script file to obtain data
  -o PATH           Output folder. Satellite data are put in and read from
                    PATH/sat/.
  -c N              Number of satellite images to download.
  -z N              Zoom level. Min=15, Max=19. See
                    libs/satellite_resolutions.csv for resolutions.
  -x N              Images have width N pixel.
  -y N              Images have height N pixel.
  -d FILETYPE_CODE  Specify file type. Will find to detect filetype
                    automatically. Will not prompt for vector conversion if
                    not given. See www.gdal.org/formats_list.html or
                    www.gdal.org/ogr_formats.html (or libs/*_formats.csv for
                    FILETYPE_CODEs.
  -n N              Accuracy of neural net. 0: lowest. 3: highest.
  --lonshift N.N    Longitudanal shift of training data.
  --latshift N.N    Lateral shift of training data .
  --shiftformat N   Format of longitudinal/lateral shift. 0: As fraction of
                    image. 1: Georeferenced unites.
  --top N           Get N most frequent classes.
  --key KEY         Set parameter key for category in GIS file to classify
                    data.
  --epsg N          EPSG format for GIS data. Is read from data if not set.
  --layer N         Number of layer to be trained on.
  --mode MODE       GPU (default) or CPU mode
  --arg1 ARG1       Argument 1 for script.
  --arg2 ARG2       Argument 2 for script.
  --arg3 ARG3       Argument 3 for script.
  --arg4 ARG4       Argument 4 for script.
  --test            Create test set.
  --no-test         Do not create test set (default)
  --background      Classify background for training (default)
  --no-background   Ignore background for training.
  --random          Use random images within GIS boundary box.
  --no-random       Only use images with features (default).
```
# Licence
See LICENCE.md
# Acknowledgements
https://github.com/alexgkendall/caffe-segnet

https://github.com/worldbank/ml4dev

# cv4ag
Computer vision application over satellite RGB tiles for agricultural land detection
24
# Install on Linux
1. Make sure package manager is allowed to get all packages
2. Clone repo: ```git clone https://github.com/worldbank/cv4ag.git```
3. ```sudo source requirements/install_linux.sh```
4. [Download tar-archive cudnn7.0](https://developer.nvidia.com/cudnn) (!) from NVidia and uncompress (```tar -xvf $/PATH/TO/TARARCHIVE```)
5. Make sure all export paths are correct (see requirements/paths-to-export.txt) and ```export``` paths
6. Clone caffe-segnet: ```git clone https://github.com/alexgkendall/caffe-segnet.git```
7. ```cd``` to ```caffe-segnet```
8. Copy ```cv4ag/requirements/Linux_Makefile.config``` to ```caffe-segnet/Makefile.config```
9. ```make all;make test;make runtest; make pycaffe```

# Install on Mac
Remark: No CUDNN and GPU support

1. Make sure you have installed homebrew. (If not ```/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"```
2. Clone repo: ```git clone https://github.com/worldbank/cv4ag.git```
3. ```cd``` to repo
4. ```source requirements/install_mac.sh```
5. ```brew update;brew cask update;brew install Caskroom/cask/cuda```
6. Clone caffe-sefnet: ```git clone https://github.com/alexgkendall/caffe-segnet.git```
7. ```cd``` to ```caffe-segnet```
8. ```echo "export PYTHONPATH=/PATH/TO/caffe-segnet/python:$PYTHONPATH">>~/.bash_profile; tail -1 ~/.bash_profile | xargs source``` (change ```/PATH/TO```)
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

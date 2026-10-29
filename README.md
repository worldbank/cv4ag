# cv4ag
Computer vision application over satellite RGB tiles for agricultural land detection

GIS polygons with land use classes (e.g. crop types) are rasterized onto Web
Mercator satellite tiles, and a U-Net with an ImageNet pretrained encoder
([segmentation_models_pytorch](https://github.com/qubvel-org/segmentation_models.pytorch))
is trained to label each pixel.

# Install
Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/). GDAL comes with the
`rasterio`/`pyogrio` wheels, no system packages are needed. Training uses an
NVIDIA GPU (CUDA) or Apple Silicon GPU (MPS) when available.

```
git clone https://github.com/worldbank/cv4ag.git; cd cv4ag
uv sync
uv run pytest        # optional: tests, including the pipeline on synthetic fields
```

Run commands with `uv run python cv4ag.py ...` (or activate `.venv`).

# Pipeline
```
uv run python cv4ag.py parse     -i fields.shp --key crop --top 5
uv run python cv4ag.py satellite -i data/fields.shp.json -c 1000 -z 17 MAPBOX_TOKEN
uv run python cv4ag.py overlay   -i data/fields.shp.json --key crop --top 5
uv run python cv4ag.py train     -i data/fields.shp.json --key crop --top 5 --test
uv run python cv4ag.py ml        -i data/fields.shp.json
```

- **parse** converts any GDAL vector format to GeoJSON (raster class maps are polygonized) and prints the most frequent classes of `--key`.
- **satellite** downloads tiles centered on features from the Mapbox Static Images API (`satellite-v9`) to `data/<name>/sat/` and records their centers in `sat/tiles.csv`.
- **overlay** writes one label image per tile to `train/` (pixel value = class id, 0 = background, 1 = most frequent class) and a visual check image to `check/`. The tile footprint is computed exactly in Web Mercator and the features are reprojected to it before rasterizing.
- **train** trains the U-Net. With `--test`, about 20% of the tiles are moved to the test set by spatial blocks; training tiles that overlap a test tile are left out so the test score is not inflated by overlapping imagery. Without `--test`, tiles already in `test/` are used for testing and never for training. Classes are weighted by median frequency balancing of their pixel counts (`--no-weights` to disable). The model with the best test mean IoU is saved to `weights/model.pt`, the log to `weights/train_log.csv`.
- **ml** classifies the images in `test/`: class ids to `out/<image>.png`, image | prediction | label to `out/<image>_vis.png`, and per-class IoU/precision/recall to `out/metrics.json`.

# Usage
```
usage: cv4ag.py [-h] [-i FILE] [-s FILE] [-o PATH] [-c N] [-z N] [-x N] [-y N]
                [-d FILETYPE_CODE] [-n N] [--lonshift N.N] [--latshift N.N]
                [--shiftformat N] [--top N] [--key KEY] [--epsg N] [--layer N]
                [--mode MODE] [--sat SAT] [--batchsize N] [--stepsize N.N]
                [--maxiter N] [--encoder ENCODER] [--seed N] [--arg1 ARG1]
                [--arg2 ARG2] [--arg3 ARG3] [--arg4 ARG4] [--test | --no-test]
                [--background | --no-background] [--random | --no-random]
                [--weights | --no-weights] [--pretrained | --no-pretrained]
                [--compares | --no-compares]
                OPTION [MAPBOX_TOKEN]

Machine Learning Framework for Agricultural Data.

positional arguments:
  OPTION             The modules to be loaded. OPTION: all - all modules
                     (except clear). parse - input file parser. satellite -
                     get satellite data. overlay - overlay classification with
                     satellite data. train - train. ml - apply machine
                     learning algorithm. clear - clear generated data from
                     previous run on input file
  MAPBOX_TOKEN       Mapbox token to download satellite images .

options:
  -h, --help         show this help message and exit
  -i FILE            Input file. Do not give if data obtained by script.
  -s FILE            Script file to obtain data
  -o PATH            Output folder. Satellite data are put in and read from
                     PATH/sat/.
  -c N               Number of satellite images to download.
  -z N               Zoom level. Min=15, Max=19. See
                     libs/zoomLevelResolution.csv for resolutions.
  -x N               Images have width N pixel.
  -y N               Images have height N pixel.
  -d FILETYPE_CODE   Specify file type. Will find to detect filetype
                     automatically. Will not prompt for vector conversion if
                     not given. See www.gdal.org/formats_list.html or
                     www.gdal.org/ogr_formats.html (or libs/*_formats.csv for
                     FILETYPE_CODEs.
  -n N               Size of neural net. 0: smallest (ResNet-18 encoder). 3:
                     largest (ResNeXt-50 encoder).
  --lonshift N.N     Longitudanal shift of training data.
  --latshift N.N     Lateral shift of training data .
  --shiftformat N    Format of longitudinal/lateral shift. 0: As fraction of
                     image. 1: Meters.
  --top N            Get N most frequent classes.
  --key KEY          Set parameter key for category in GIS file to classify
                     data.
  --epsg N           EPSG format for GIS data. Is read from data if not set.
  --layer N          Number of layers to be trained on.
  --mode MODE        GPU (default) or CPU mode
  --sat SAT          Folder with training satellite images, if not in standard
                     location.
  --batchsize N      Size of training batch (default 8)
  --stepsize N.N     Learning rate (default 5e-4)
  --maxiter N        Maximum iterations at training stage
  --encoder ENCODER  Encoder of the U-Net, overrides -n (any
                     segmentation_models_pytorch encoder, e.g. resnet34)
  --seed N           Random seed for the train/test split and training
  --arg1 ARG1        Argument 1 for script.
  --arg2 ARG2        Argument 2 for script.
  --arg3 ARG3        Argument 3 for script.
  --arg4 ARG4        Argument 4 for script.
  --test             Create test set.
  --no-test          Do not create test set (default)
  --background       Classify background for training (default)
  --no-background    Ignore background for training.
  --random           Use random images within GIS boundary box.
  --no-random        Only use images with features (default).
  --weights          Weight classes inversely to their pixel frequency
                     (default).
  --no-weights       Weight all classes equally.
  --pretrained       Start from ImageNet weights (default).
  --no-pretrained    Train from scratch.
  --compares         Compare classified results with labels
  --no-compares      Do not compare classified results with labels
```

# Licence
See LICENCE.md
# Acknowledgements
https://github.com/qubvel-org/segmentation_models.pytorch (earlier versions: https://github.com/alexgkendall/caffe-segnet)

https://github.com/worldbank/ml4dev

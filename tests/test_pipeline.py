'''overlay -> train -> ml on synthetic fields'''
import json
import os

import numpy as np
from PIL import Image

from modules import applyml, overlay, train
from tests.synthetic import make_dataset


def test_pipeline_on_synthetic_fields(tmp_path):
    inputFile, outputFolder, truth = make_dataset(str(tmp_path))

    overlay.overlay(outputFolder, inputFile, top=3, key='crop', zoomLevel=16)
    trainpath = os.path.join(outputFolder, 'fields', 'train')
    for name, expected in truth.items():
        label = np.asarray(Image.open(os.path.join(trainpath, name[:-4] + 'train.png')))
        # labels line up with the independently rendered imagery
        assert (label == expected).mean() > 0.995, name
    assert os.path.isfile(os.path.join(trainpath, 'footprints.csv'))

    train.train(outputFolder, inputFile, key='crop', top=3, encoder='resnet18', pretrained=False,
                maxiter=40, batchsize=4, mode='cpu', createTest=True)
    subpath = os.path.join(outputFolder, 'fields')
    assert os.path.isfile(os.path.join(subpath, 'weights', 'model.pt'))
    with open(os.path.join(subpath, 'meta_classlabels.txt')) as f:
        assert f.read().split('\n')[:2] == ['0\tBackground', '1\tcorn']

    applyml.apply(outputFolder, inputFile, mode='cpu')
    with open(os.path.join(subpath, 'out', 'metrics.json')) as f:
        metrics = json.load(f)
    assert 0 <= metrics['miou'] <= 1
    tests = [f for f in os.listdir(os.path.join(subpath, 'test')) if f.endswith('.png')]
    assert tests and all(os.path.isfile(os.path.join(subpath, 'out', f)) for f in tests)

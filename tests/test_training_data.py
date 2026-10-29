import numpy as np
import pytest
from PIL import Image

from modules.segmentation import IGNORE_INDEX, confusion_matrix, scores
from modules.train import classWeights, spatialSplit


def grid_footprints(n=20, size=100.0, overlap=0.5):
    '''n x n tiles of the given size, overlapping their neighbours by overlap'''
    step = size * (1 - overlap)
    return {'t_%d_%d.png' % (i, j): ('EPSG:3857', (i * step, j * step, i * step + size, j * step + size))
            for i in range(n) for j in range(n)}


def test_spatial_split_keeps_test_tiles_apart_from_training_tiles():
    footprints = grid_footprints()
    names = sorted(footprints)
    train, test, dropped = spatialSplit(names, footprints, fraction=0.2, seed=1)
    assert set(train) | set(test) | set(dropped) == set(names)
    assert not set(train) & set(test)
    assert 0.15 <= len(test) / len(names) <= 0.35
    for t in train:
        w, s, e, n = footprints[t][1]
        for u in test:
            tw, ts, te, tn = footprints[u][1]
            assert not (tw < e and te > w and ts < n and tn > s), (t, u)
    assert spatialSplit(names, footprints, fraction=0.2, seed=1) == (train, test, dropped)


def test_spatial_split_of_a_small_area_still_has_training_tiles():
    footprints = grid_footprints(n=4, overlap=0)
    train, test, _ = spatialSplit(sorted(footprints), footprints, fraction=0.2)
    assert train and test


def test_class_weights_favour_rare_classes(tmp_path):
    label = np.zeros((10, 100), dtype=np.uint8)
    label[:, :10] = 1   # 10%
    label[:, 10:40] = 2  # 30%
    label[:, 40:41] = 3  # 1%, rest background
    Image.fromarray(label).save(tmp_path / 'l.png')
    weights, counts = classWeights([(None, tmp_path / 'l.png')], 5)
    assert counts.tolist() == [590, 100, 300, 10, 0]
    assert weights[3] > weights[1] > weights[2] > weights[0]
    assert weights[4] == 1  # absent class
    weights, counts = classWeights([(None, tmp_path / 'l.png')], 5, ignorebackground=True)
    assert counts[0] == 0
    assert weights[1] == pytest.approx(1)  # median class


def test_scores_skip_ignored_pixels_and_absent_classes():
    label = np.array([[0, 1, 1, IGNORE_INDEX]], dtype=np.uint8)
    pred = np.array([[0, 1, 2, 2]], dtype=np.uint8)
    cm = confusion_matrix(pred, label, 3)
    assert cm.tolist() == [[1, 0, 0], [0, 1, 1], [0, 0, 0]]
    result = scores(cm, ['Background', 'a', 'b'])
    assert [c['class'] for c in result['classes']] == ['Background', 'a']
    assert result['classes'][1]['iou'] == pytest.approx(0.5)
    assert result['miou'] == pytest.approx(0.75)
    assert result['accuracy'] == pytest.approx(2 / 3)

solver=\
'''net: "PATH_TO_TRAINPROTOTXT"  		# Change this to the absolute path to your model file
test_initialization: false
test_iter: 1
test_interval: 10000000
base_lr: INSERT_BASE_LR #Value 0.001 to 0.1
lr_policy: "step"
gamma: 1.0
stepsize: 10000000
display: 20
momentum: 0.9
max_iter: INSERT_MAX_ITER #10000 to 40000
weight_decay: 0.0005
snapshot: 1000
snapshot_prefix: "PATH_TO_OUTPUT"  	# Change this to the absolute path to where you wish to output solver snapshots
solver_mode: OPTION_GPU_OR_CPU'''

nets=[\
'''name: "segnet"
layer {
  name: "data"
  type: "DATATYPE"
  top: "data"
  top: "label"
  dense_image_data_param {
    source: "PATH_TO_TRAINTXT"	# Change this to the absolute path to your data file
    batch_size: BATCHSIZE   			# Change this number to a batch size that will fit on your GPU
    shuffle: true
  }
}
layer {
  name: "norm"
  type: "LRN"
  bottom: "data"
  top: "norm"
  lrn_param {
    local_size: 5
    alpha: 0.0001
    beta: 0.75
  }
}
layer {
  name: "conv1"
  type: "Convolution"
  bottom: "norm"
  top: "conv1"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv1"
  top: "conv1"
  name: "conv1_bn"
  type: "BN"
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "relu1"
  type: "ReLU"
  bottom: "conv1"
  top: "conv1"
}
layer {
  name: "pool1"
  type: "Pooling"
  bottom: "conv1"
  top: "pool1"
  top: "pool1_mask"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  name: "conv2"
  type: "Convolution"
  bottom: "pool1"
  top: "conv2"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv2"
  top: "conv2"
  name: "conv2_bn"
  type: "BN"
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "relu2"
  type: "ReLU"
  bottom: "conv2"
  top: "conv2"
}
layer {
  name: "pool2"
  type: "Pooling"
  bottom: "conv2"
  top: "pool2"
  top: "pool2_mask"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  name: "conv3"
  type: "Convolution"
  bottom: "pool2"
  top: "conv3"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv3"
  top: "conv3"
  name: "conv3_bn"
  type: "BN"
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "relu3"
  type: "ReLU"
  bottom: "conv3"
  top: "conv3"
}
layer {
  name: "pool3"
  type: "Pooling"
  bottom: "conv3"
  top: "pool3"
  top: "pool3_mask"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  name: "conv4"
  type: "Convolution"
  bottom: "pool3"
  top: "conv4"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv4"
  top: "conv4"
  name: "conv4_bn"
  type: "BN"
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "relu4"
  type: "ReLU"
  bottom: "conv4"
  top: "conv4"
}
layer {
  name: "pool4"
  type: "Pooling"
  bottom: "conv4"
  top: "pool4"
  top: "pool4_mask"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  name: "upsample4"
  type: "Upsample"
  bottom: "pool4"
  bottom: "pool4_mask"
  top: "upsample4"
  upsample_param {
    scale: 2
    pad_out_h: true
  }
}
layer {
  name: "conv_decode4"
  type: "Convolution"
  bottom: "upsample4"
  top: "conv_decode4"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv_decode4"
  top: "conv_decode4"
  name: "conv_decode4_bn"
  type: "BN"
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "upsample3"
  type: "Upsample"
  bottom: "conv_decode4"
  bottom: "pool3_mask"
  top: "upsample3"
  upsample_param {
    scale: 2
  }
}
layer {
  name: "conv_decode3"
  type: "Convolution"
  bottom: "upsample3"
  top: "conv_decode3"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv_decode3"
  top: "conv_decode3"
  name: "conv_decode3_bn"
  type: "BN"
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "upsample2"
  type: "Upsample"
  bottom: "conv_decode3"
  bottom: "pool2_mask"
  top: "upsample2"
  upsample_param {
    scale: 2
  }
}
layer {
  name: "conv_decode2"
  type: "Convolution"
  bottom: "upsample2"
  top: "conv_decode2"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv_decode2"
  top: "conv_decode2"
  name: "conv_decode2_bn"
  type: "BN"
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "upsample1"
  type: "Upsample"
  bottom: "conv_decode2"
  bottom: "pool1_mask"
  top: "upsample1"
  upsample_param {
    scale: 2
  }
}
layer {
  name: "conv_decode1"
  type: "Convolution"
  bottom: "upsample1"
  top: "conv_decode1"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv_decode1"
  top: "conv_decode1"
  name: "conv_decode1_bn"
  type: "BN"
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "conv_classifier"
  type: "Convolution"
  bottom: "conv_decode1"
  top: "conv_classifier"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: INSERT_NUM_CLASSES
    kernel_size: 1
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  name: "loss"
  type: "SoftmaxWithLoss"
  bottom: "conv_classifier"
  bottom: "label"
  top: "loss"
  softmax_param {engine: CAFFE}
  loss_param: {
    weight_by_label_freqs: true
    INSERT_IGNORE_LABEL
    INSERT_CLASS_WEIGHTING
  }
}
layer {
  name: "accuracy"
  type: "Accuracy"
  bottom: "conv_classifier"
  bottom: "label"
  top: "accuracy"
  top: "per_class_accuracy"
}''',\
'''
name: "VGG_ILSVRC_16_layer"
layer {
  name: "data"
  type: "DATATYPE"
  top: "data"
  top: "label"
  dense_image_data_param {
    source: "PATH_TO_TRAINTXT"	# Change this to the absolute path to your data file
    batch_size: BATCHSIZE   			# Change this number to a batch size that will fit on your GPU
    shuffle: true
  }
}
layer {
  bottom: "data"
  top: "conv1_1"
  name: "conv1_1"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 64
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv1_1"
  top: "conv1_1"
  name: "conv1_1_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv1_1"
  top: "conv1_1"
  name: "relu1_1"
  type: "ReLU"
}
layer {
  bottom: "conv1_1"
  top: "conv1_2"
  name: "conv1_2"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 64
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv1_2"
  top: "conv1_2"
  name: "conv1_2_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv1_2"
  top: "conv1_2"
  name: "relu1_2"
  type: "ReLU"
}
layer {
  bottom: "conv1_2"
  top: "pool1"
  top: "pool1_mask"
  name: "pool1"
  type: "Pooling"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  bottom: "pool1"
  top: "conv2_1"
  name: "conv2_1"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 128
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv2_1"
  top: "conv2_1"
  name: "conv2_1_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv2_1"
  top: "conv2_1"
  name: "relu2_1"
  type: "ReLU"
}
layer {
  bottom: "conv2_1"
  top: "conv2_2"
  name: "conv2_2"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 128
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv2_2"
  top: "conv2_2"
  name: "conv2_2_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv2_2"
  top: "conv2_2"
  name: "relu2_2"
  type: "ReLU"
}
layer {
  bottom: "conv2_2"
  top: "pool2"
  top: "pool2_mask"
  name: "pool2"
  type: "Pooling"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  bottom: "pool2"
  top: "conv3_1"
  name: "conv3_1"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 256
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv3_1"
  top: "conv3_1"
  name: "conv3_1_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv3_1"
  top: "conv3_1"
  name: "relu3_1"
  type: "ReLU"
}
layer {
  bottom: "conv3_1"
  top: "conv3_2"
  name: "conv3_2"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 256
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv3_2"
  top: "conv3_2"
  name: "conv3_2_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv3_2"
  top: "conv3_2"
  name: "relu3_2"
  type: "ReLU"
}
layer {
  bottom: "conv3_2"
  top: "conv3_3"
  name: "conv3_3"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 256
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv3_3"
  top: "conv3_3"
  name: "conv3_3_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv3_3"
  top: "conv3_3"
  name: "relu3_3"
  type: "ReLU"
}
layer {
  bottom: "conv3_3"
  top: "pool3"
  top: "pool3_mask"
  name: "pool3"
  type: "Pooling"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  bottom: "pool3"
  top: "conv4_1"
  name: "conv4_1"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv4_1"
  top: "conv4_1"
  name: "conv4_1_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv4_1"
  top: "conv4_1"
  name: "relu4_1"
  type: "ReLU"
}
layer {
  bottom: "conv4_1"
  top: "conv4_2"
  name: "conv4_2"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv4_2"
  top: "conv4_2"
  name: "conv4_2_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv4_2"
  top: "conv4_2"
  name: "relu4_2"
  type: "ReLU"
}
layer {
  bottom: "conv4_2"
  top: "conv4_3"
  name: "conv4_3"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv4_3"
  top: "conv4_3"
  name: "conv4_3_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv4_3"
  top: "conv4_3"
  name: "relu4_3"
  type: "ReLU"
}
layer {
  bottom: "conv4_3"
  top: "pool4"
  top: "pool4_mask"
  name: "pool4"
  type: "Pooling"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  bottom: "pool4"
  top: "conv5_1"
  name: "conv5_1"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv5_1"
  top: "conv5_1"
  name: "conv5_1_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv5_1"
  top: "conv5_1"
  name: "relu5_1"
  type: "ReLU"
}
layer {
  bottom: "conv5_1"
  top: "conv5_2"
  name: "conv5_2"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv5_2"
  top: "conv5_2"
  name: "conv5_2_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv5_2"
  top: "conv5_2"
  name: "relu5_2"
  type: "ReLU"
}
layer {
  bottom: "conv5_2"
  top: "conv5_3"
  name: "conv5_3"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv5_3"
  top: "conv5_3"
  name: "conv5_3_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv5_3"
  top: "conv5_3"
  name: "relu5_3"
  type: "ReLU"
}
layer {
  bottom: "conv5_3"
  top: "pool5"
  top: "pool5_mask"
  name: "pool5"
  type: "Pooling"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  name: "upsample5"
  type: "Upsample"
  bottom: "pool5"
  top: "pool5_D"
  bottom: "pool5_mask"
  upsample_param {
    scale: 2
    upsample_w: UPSAMPLE_W_SMALL
    upsample_h: UPSAMPLE_H_SMALL
  }
}
layer {
  bottom: "pool5_D"
  top: "conv5_3_D"
  name: "conv5_3_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv5_3_D"
  top: "conv5_3_D"
  name: "conv5_3_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv5_3_D"
  top: "conv5_3_D"
  name: "relu5_3_D"
  type: "ReLU"
}

layer {
  bottom: "conv5_3_D"
  top: "conv5_2_D"
  name: "conv5_2_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv5_2_D"
  top: "conv5_2_D"
  name: "conv5_2_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv5_2_D"
  top: "conv5_2_D"
  name: "relu5_2_D"
  type: "ReLU"
}
layer {
  bottom: "conv5_2_D"
  top: "conv5_1_D"
  name: "conv5_1_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv5_1_D"
  top: "conv5_1_D"
  name: "conv5_1_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv5_1_D"
  top: "conv5_1_D"
  name: "relu5_1_D"
  type: "ReLU"
}
layer {
  name: "upsample4"
  type: "Upsample"
  bottom: "conv5_1_D"
  top: "pool4_D"
  bottom: "pool4_mask"
  upsample_param {
    scale: 2
    upsample_w: UPSAMPLE_W_LARGE
    upsample_h: UPSAMPLE_H_LARGE
  }
}
layer {
  bottom: "pool4_D"
  top: "conv4_3_D"
  name: "conv4_3_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv4_3_D"
  top: "conv4_3_D"
  name: "conv4_3_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv4_3_D"
  top: "conv4_3_D"
  name: "relu4_3_D"
  type: "ReLU"
}
layer {
  bottom: "conv4_3_D"
  top: "conv4_2_D"
  name: "conv4_2_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv4_2_D"
  top: "conv4_2_D"
  name: "conv4_2_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv4_2_D"
  top: "conv4_2_D"
  name: "relu4_2_D"
  type: "ReLU"
}
layer {
  bottom: "conv4_2_D"
  top: "conv4_1_D"
  name: "conv4_1_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 256
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv4_1_D"
  top: "conv4_1_D"
  name: "conv4_1_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv4_1_D"
  top: "conv4_1_D"
  name: "relu4_1_D"
  type: "ReLU"
}
layer {
  name: "upsample3"
  type: "Upsample"
  bottom: "conv4_1_D"
  top: "pool3_D"
  bottom: "pool3_mask"
  upsample_param {
    scale: 2
  }
}
layer {
  bottom: "pool3_D"
  top: "conv3_3_D"
  name: "conv3_3_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 256
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv3_3_D"
  top: "conv3_3_D"
  name: "conv3_3_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv3_3_D"
  top: "conv3_3_D"
  name: "relu3_3_D"
  type: "ReLU"
}
layer {
  bottom: "conv3_3_D"
  top: "conv3_2_D"
  name: "conv3_2_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 256
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv3_2_D"
  top: "conv3_2_D"
  name: "conv3_2_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv3_2_D"
  top: "conv3_2_D"
  name: "relu3_2_D"
  type: "ReLU"
}
layer {
  bottom: "conv3_2_D"
  top: "conv3_1_D"
  name: "conv3_1_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 128
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv3_1_D"
  top: "conv3_1_D"
  name: "conv3_1_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv3_1_D"
  top: "conv3_1_D"
  name: "relu3_1_D"
  type: "ReLU"
}
layer {
  name: "upsample2"
  type: "Upsample"
  bottom: "conv3_1_D"
  top: "pool2_D"
  bottom: "pool2_mask"
  upsample_param {
    scale: 2
  }
}
layer {
  bottom: "pool2_D"
  top: "conv2_2_D"
  name: "conv2_2_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 128
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv2_2_D"
  top: "conv2_2_D"
  name: "conv2_2_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv2_2_D"
  top: "conv2_2_D"
  name: "relu2_2_D"
  type: "ReLU"
}
layer {
  bottom: "conv2_2_D"
  top: "conv2_1_D"
  name: "conv2_1_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 64
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv2_1_D"
  top: "conv2_1_D"
  name: "conv2_1_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv2_1_D"
  top: "conv2_1_D"
  name: "relu2_1_D"
  type: "ReLU"
}
layer {
  name: "upsample1"
  type: "Upsample"
  bottom: "conv2_1_D"
  top: "pool1_D"
  bottom: "pool1_mask"
  upsample_param {
    scale: 2
  }
}
layer {
  bottom: "pool1_D"
  top: "conv1_2_D"
  name: "conv1_2_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 64
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv1_2_D"
  top: "conv1_2_D"
  name: "conv1_2_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv1_2_D"
  top: "conv1_2_D"
  name: "relu1_2_D"
  type: "ReLU"
}
layer {
  bottom: "conv1_2_D"
  top: "conv1_1_D"
  name: "conv1_1_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: INSERT_NUM_CLASSES
    pad: 1
    kernel_size: 3
  }
}
layer {
  name: "loss"
  type: "SoftmaxWithLoss"
  bottom: "conv1_1_D"
  bottom: "label"
  top: "loss"
  softmax_param {engine: CAFFE}
  loss_param: {
    weight_by_label_freqs: true
    INSERT_IGNORE_LABEL
    INSERT_CLASS_WEIGHTING
  }
}
layer {
  name: "accuracy"
  type: "Accuracy"
  bottom: "conv1_1_D"
  bottom: "label"
  top: "accuracy"
  top: "per_class_accuracy"
}''']

inferences=[\
'''name: "segnet"
layer {
  name: "data"
  type: "DATATYPE"
  top: "data"
  top: "label"
  dense_image_data_param {
    source: "PATH_TO_TESTTXT"	# Change this to the absolute path to your data file
    batch_size: BATCHSIZE
  }
}
layer {
  name: "norm"
  type: "LRN"
  bottom: "data"
  top: "norm"
  lrn_param {
    local_size: 5
    alpha: 0.0001
    beta: 0.75
  }
}
layer {
  name: "conv1"
  type: "Convolution"
  bottom: "norm"
  top: "conv1"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv1"
  top: "conv1"
  name: "conv1_bn"
  type: "BN"
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "relu1"
  type: "ReLU"
  bottom: "conv1"
  top: "conv1"
}
layer {
  name: "pool1"
  type: "Pooling"
  bottom: "conv1"
  top: "pool1"
  top: "pool1_mask"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  name: "conv2"
  type: "Convolution"
  bottom: "pool1"
  top: "conv2"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv2"
  top: "conv2"
  name: "conv2_bn"
  type: "BN"
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "relu2"
  type: "ReLU"
  bottom: "conv2"
  top: "conv2"
}
layer {
  name: "pool2"
  type: "Pooling"
  bottom: "conv2"
  top: "pool2"
  top: "pool2_mask"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  name: "conv3"
  type: "Convolution"
  bottom: "pool2"
  top: "conv3"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv3"
  top: "conv3"
  name: "conv3_bn"
  type: "BN"
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "relu3"
  type: "ReLU"
  bottom: "conv3"
  top: "conv3"
}
layer {
  name: "pool3"
  type: "Pooling"
  bottom: "conv3"
  top: "pool3"
  top: "pool3_mask"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  name: "conv4"
  type: "Convolution"
  bottom: "pool3"
  top: "conv4"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv4"
  top: "conv4"
  name: "conv4_bn"
  type: "BN"
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "relu4"
  type: "ReLU"
  bottom: "conv4"
  top: "conv4"
}
layer {
  name: "pool4"
  type: "Pooling"
  bottom: "conv4"
  top: "pool4"
  top: "pool4_mask"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  name: "upsample4"
  type: "Upsample"
  bottom: "pool4"
  bottom: "pool4_mask"
  top: "upsample4"
  upsample_param {
    scale: 2
    pad_out_h: true
  }
}
layer {
  name: "conv_decode4"
  type: "Convolution"
  bottom: "upsample4"
  top: "conv_decode4"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv_decode4"
  top: "conv_decode4"
  name: "conv_decode4_bn"
  type: "BN"
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "upsample3"
  type: "Upsample"
  bottom: "conv_decode4"
  bottom: "pool3_mask"
  top: "upsample3"
  upsample_param {
    scale: 2
  }
}
layer {
  name: "conv_decode3"
  type: "Convolution"
  bottom: "upsample3"
  top: "conv_decode3"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv_decode3"
  top: "conv_decode3"
  name: "conv_decode3_bn"
  type: "BN"
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "upsample2"
  type: "Upsample"
  bottom: "conv_decode3"
  bottom: "pool2_mask"
  top: "upsample2"
  upsample_param {
    scale: 2
  }
}
layer {
  name: "conv_decode2"
  type: "Convolution"
  bottom: "upsample2"
  top: "conv_decode2"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv_decode2"
  top: "conv_decode2"
  name: "conv_decode2_bn"
  type: "BN"
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "upsample1"
  type: "Upsample"
  bottom: "conv_decode2"
  bottom: "pool1_mask"
  top: "upsample1"
  upsample_param {
    scale: 2
  }
}
layer {
  name: "conv_decode1"
  type: "Convolution"
  bottom: "upsample1"
  top: "conv_decode1"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: 64
    kernel_size: 7
    pad: 3
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  bottom: "conv_decode1"
  top: "conv_decode1"
  name: "conv_decode1_bn"
  type: "BN"
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  name: "conv_classifier"
  type: "Convolution"
  bottom: "conv_decode1"
  top: "conv_classifier"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    num_output: INSERT_NUM_CLASSES
    kernel_size: 1
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
  }
}
layer {
  name: "prob"
  type: "Softmax"
  bottom: "conv_classifier"
  top: "prob"
  softmax_param {engine: CAFFE}
}''',\
'''name: "VGG_ILSVRC_16_layer"
layer {
  name: "data"
  type: "DATATYPE"
  top: "data"
  top: "label"
  dense_image_data_param {
    source: "PATH_TO_TESTTXT"	# Change this to the absolute path to your data file
    batch_size: BATCHSIZE
  }
}
layer {
  bottom: "data"
  top: "conv1_1"
  name: "conv1_1"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 64
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv1_1"
  top: "conv1_1"
  name: "conv1_1_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv1_1"
  top: "conv1_1"
  name: "relu1_1"
  type: "ReLU"
}
layer {
  bottom: "conv1_1"
  top: "conv1_2"
  name: "conv1_2"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 64
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv1_2"
  top: "conv1_2"
  name: "conv1_2_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv1_2"
  top: "conv1_2"
  name: "relu1_2"
  type: "ReLU"
}
layer {
  bottom: "conv1_2"
  top: "pool1"
  top: "pool1_mask"
  name: "pool1"
  type: "Pooling"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  bottom: "pool1"
  top: "conv2_1"
  name: "conv2_1"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 128
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv2_1"
  top: "conv2_1"
  name: "conv2_1_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv2_1"
  top: "conv2_1"
  name: "relu2_1"
  type: "ReLU"
}
layer {
  bottom: "conv2_1"
  top: "conv2_2"
  name: "conv2_2"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 128
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv2_2"
  top: "conv2_2"
  name: "conv2_2_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv2_2"
  top: "conv2_2"
  name: "relu2_2"
  type: "ReLU"
}
layer {
  bottom: "conv2_2"
  top: "pool2"
  top: "pool2_mask"
  name: "pool2"
  type: "Pooling"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  bottom: "pool2"
  top: "conv3_1"
  name: "conv3_1"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 256
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv3_1"
  top: "conv3_1"
  name: "conv3_1_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv3_1"
  top: "conv3_1"
  name: "relu3_1"
  type: "ReLU"
}
layer {
  bottom: "conv3_1"
  top: "conv3_2"
  name: "conv3_2"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 256
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv3_2"
  top: "conv3_2"
  name: "conv3_2_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv3_2"
  top: "conv3_2"
  name: "relu3_2"
  type: "ReLU"
}
layer {
  bottom: "conv3_2"
  top: "conv3_3"
  name: "conv3_3"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 256
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv3_3"
  top: "conv3_3"
  name: "conv3_3_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv3_3"
  top: "conv3_3"
  name: "relu3_3"
  type: "ReLU"
}
layer {
  bottom: "conv3_3"
  top: "pool3"
  top: "pool3_mask"
  name: "pool3"
  type: "Pooling"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  bottom: "pool3"
  top: "conv4_1"
  name: "conv4_1"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv4_1"
  top: "conv4_1"
  name: "conv4_1_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv4_1"
  top: "conv4_1"
  name: "relu4_1"
  type: "ReLU"
}
layer {
  bottom: "conv4_1"
  top: "conv4_2"
  name: "conv4_2"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv4_2"
  top: "conv4_2"
  name: "conv4_2_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv4_2"
  top: "conv4_2"
  name: "relu4_2"
  type: "ReLU"
}
layer {
  bottom: "conv4_2"
  top: "conv4_3"
  name: "conv4_3"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv4_3"
  top: "conv4_3"
  name: "conv4_3_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv4_3"
  top: "conv4_3"
  name: "relu4_3"
  type: "ReLU"
}
layer {
  bottom: "conv4_3"
  top: "pool4"
  top: "pool4_mask"
  name: "pool4"
  type: "Pooling"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  bottom: "pool4"
  top: "conv5_1"
  name: "conv5_1"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv5_1"
  top: "conv5_1"
  name: "conv5_1_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv5_1"
  top: "conv5_1"
  name: "relu5_1"
  type: "ReLU"
}
layer {
  bottom: "conv5_1"
  top: "conv5_2"
  name: "conv5_2"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv5_2"
  top: "conv5_2"
  name: "conv5_2_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv5_2"
  top: "conv5_2"
  name: "relu5_2"
  type: "ReLU"
}
layer {
  bottom: "conv5_2"
  top: "conv5_3"
  name: "conv5_3"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv5_3"
  top: "conv5_3"
  name: "conv5_3_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv5_3"
  top: "conv5_3"
  name: "relu5_3"
  type: "ReLU"
}
layer {
  bottom: "conv5_3"
  top: "pool5"
  top: "pool5_mask"
  name: "pool5"
  type: "Pooling"
  pooling_param {
    pool: MAX
    kernel_size: 2
    stride: 2
  }
}
layer {
  name: "upsample5"
  type: "Upsample"
  bottom: "pool5"
  top: "pool5_D"
  bottom: "pool5_mask"
  upsample_param {
    scale: 2
    upsample_w: UPSAMPLE_W_SMALL
    upsample_h: UPSAMPLE_H_SMALL
  }
}
layer {
  bottom: "pool5_D"
  top: "conv5_3_D"
  name: "conv5_3_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv5_3_D"
  top: "conv5_3_D"
  name: "conv5_3_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv5_3_D"
  top: "conv5_3_D"
  name: "relu5_3_D"
  type: "ReLU"
}

layer {
  bottom: "conv5_3_D"
  top: "conv5_2_D"
  name: "conv5_2_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv5_2_D"
  top: "conv5_2_D"
  name: "conv5_2_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv5_2_D"
  top: "conv5_2_D"
  name: "relu5_2_D"
  type: "ReLU"
}
layer {
  bottom: "conv5_2_D"
  top: "conv5_1_D"
  name: "conv5_1_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv5_1_D"
  top: "conv5_1_D"
  name: "conv5_1_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv5_1_D"
  top: "conv5_1_D"
  name: "relu5_1_D"
  type: "ReLU"
}
layer {
  name: "upsample4"
  type: "Upsample"
  bottom: "conv5_1_D"
  top: "pool4_D"
  bottom: "pool4_mask"
  upsample_param {
    scale: 2
    upsample_w: UPSAMPLE_W_LARGE
    upsample_h: UPSAMPLE_W_SMALL
  }
}
layer {
  bottom: "pool4_D"
  top: "conv4_3_D"
  name: "conv4_3_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv4_3_D"
  top: "conv4_3_D"
  name: "conv4_3_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv4_3_D"
  top: "conv4_3_D"
  name: "relu4_3_D"
  type: "ReLU"
}
layer {
  bottom: "conv4_3_D"
  top: "conv4_2_D"
  name: "conv4_2_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 512
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv4_2_D"
  top: "conv4_2_D"
  name: "conv4_2_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv4_2_D"
  top: "conv4_2_D"
  name: "relu4_2_D"
  type: "ReLU"
}
layer {
  bottom: "conv4_2_D"
  top: "conv4_1_D"
  name: "conv4_1_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 256
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv4_1_D"
  top: "conv4_1_D"
  name: "conv4_1_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv4_1_D"
  top: "conv4_1_D"
  name: "relu4_1_D"
  type: "ReLU"
}
layer {
  name: "upsample3"
  type: "Upsample"
  bottom: "conv4_1_D"
  top: "pool3_D"
  bottom: "pool3_mask"
  upsample_param {
    scale: 2
  }
}
layer {
  bottom: "pool3_D"
  top: "conv3_3_D"
  name: "conv3_3_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 256
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv3_3_D"
  top: "conv3_3_D"
  name: "conv3_3_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv3_3_D"
  top: "conv3_3_D"
  name: "relu3_3_D"
  type: "ReLU"
}
layer {
  bottom: "conv3_3_D"
  top: "conv3_2_D"
  name: "conv3_2_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 256
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv3_2_D"
  top: "conv3_2_D"
  name: "conv3_2_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv3_2_D"
  top: "conv3_2_D"
  name: "relu3_2_D"
  type: "ReLU"
}
layer {
  bottom: "conv3_2_D"
  top: "conv3_1_D"
  name: "conv3_1_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 128
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv3_1_D"
  top: "conv3_1_D"
  name: "conv3_1_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv3_1_D"
  top: "conv3_1_D"
  name: "relu3_1_D"
  type: "ReLU"
}
layer {
  name: "upsample2"
  type: "Upsample"
  bottom: "conv3_1_D"
  top: "pool2_D"
  bottom: "pool2_mask"
  upsample_param {
    scale: 2
  }
}
layer {
  bottom: "pool2_D"
  top: "conv2_2_D"
  name: "conv2_2_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 128
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv2_2_D"
  top: "conv2_2_D"
  name: "conv2_2_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv2_2_D"
  top: "conv2_2_D"
  name: "relu2_2_D"
  type: "ReLU"
}
layer {
  bottom: "conv2_2_D"
  top: "conv2_1_D"
  name: "conv2_1_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 64
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv2_1_D"
  top: "conv2_1_D"
  name: "conv2_1_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv2_1_D"
  top: "conv2_1_D"
  name: "relu2_1_D"
  type: "ReLU"
}
layer {
  name: "upsample1"
  type: "Upsample"
  bottom: "conv2_1_D"
  top: "pool1_D"
  bottom: "pool1_mask"
  upsample_param {
    scale: 2
  }
}
layer {
  bottom: "pool1_D"
  top: "conv1_2_D"
  name: "conv1_2_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: 64
    pad: 1
    kernel_size: 3
  }
}
layer {
  bottom: "conv1_2_D"
  top: "conv1_2_D"
  name: "conv1_2_D_bn"
  type: "BN"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 1
    decay_mult: 0
  }
  bn_param {
	bn_mode: INFERENCE
	scale_filler {
	  type: "constant"
	  value: 1
	}
	shift_filler {
	  type: "constant"
	  value: 0.001
	}
 }
}
layer {
  bottom: "conv1_2_D"
  top: "conv1_2_D"
  name: "relu1_2_D"
  type: "ReLU"
}
layer {
  bottom: "conv1_2_D"
  top: "conv1_1_D"
  name: "conv1_1_D"
  type: "Convolution"
  param {
    lr_mult: 1
    decay_mult: 1
  }
  param {
    lr_mult: 2
    decay_mult: 0
  }
  convolution_param {
    weight_filler {
      type: "msra"
    }
    bias_filler {
      type: "constant"
    }
    num_output: INSERT_NUM_CLASSES
    pad: 1
    kernel_size: 3
  }
}
layer {
  name: "prob"
  type: "Softmax"
  bottom: "conv1_1_D"
  top: "prob"
  softmax_param {engine: CAFFE}
}''']

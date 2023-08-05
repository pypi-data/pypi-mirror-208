import torch_hrp as thrp
import torch
import numpy as np


def test_1():
    """ The initialized hyperplane should have always the same weights
          for the given default PRNG seed.
    """
    BATCH_SIZE = 32
    NUM_FEATURES = 64
    OUTPUT_SIZE = 1024
    # demo inputs
    inputs = torch.randn(size=(BATCH_SIZE, NUM_FEATURES))
    # instantiate layer without telling the seed
    layer = thrp.HashedRandomProjection(
        output_size=OUTPUT_SIZE, input_size=inputs.shape[-1])
    outputs = layer(inputs)
    assert outputs.shape == (BATCH_SIZE, OUTPUT_SIZE)
    # instantiate another layer
    layer2 = thrp.HashedRandomProjection(
        output_size=OUTPUT_SIZE, input_size=inputs.shape[-1])
    outputs2 = layer2(inputs)
    assert outputs2.shape == (BATCH_SIZE, OUTPUT_SIZE)
    assert torch.all(outputs == outputs2)


def test_2():
    """ Different PRNG seeds should lead to different hyperplanes """
    BATCH_SIZE = 32
    NUM_FEATURES = 64
    OUTPUT_SIZE = 1024
    # demo inputs
    inputs = torch.randn(size=(BATCH_SIZE, NUM_FEATURES))
    # instantiate layer without telling the seed
    layer = thrp.HashedRandomProjection(
        output_size=OUTPUT_SIZE, input_size=inputs.shape[-1],
        random_state=23)
    outputs = layer(inputs)
    assert outputs.shape == (BATCH_SIZE, OUTPUT_SIZE)
    # instantiate another layer
    layer2 = thrp.HashedRandomProjection(
        output_size=OUTPUT_SIZE, input_size=inputs.shape[-1],
        random_state=42)
    outputs2 = layer2(inputs)
    assert outputs2.shape == (BATCH_SIZE, OUTPUT_SIZE)
    assert not torch.all(outputs == outputs2)
    assert not torch.all(layer.hyperplane == layer2.hyperplane)


def test_3():
    """ The hyperplane can be set as input argument """
    BATCH_SIZE = 32
    NUM_FEATURES = 64
    OUTPUT_SIZE = 1024
    # demo inputs
    inputs = torch.randn(size=(BATCH_SIZE, NUM_FEATURES))
    # create hyperplane as numpy array
    myhyperplane = np.random.randn(
        NUM_FEATURES, OUTPUT_SIZE).astype(np.float32)
    layer = thrp.HashedRandomProjection(hyperplane=myhyperplane)
    outputs = layer(inputs)
    assert outputs.shape == (BATCH_SIZE, OUTPUT_SIZE)
    assert torch.all(layer.hyperplane == torch.tensor(myhyperplane))

import torch
from typing import List


class HashedRandomProjection(torch.nn.Module):
    """ The HRP layer

    Parameters:
    -----------
    hyperplane : torch.Tensor (Default: None)
        An existing matrix with weights

    random_state : int (Default: 42)
        Random seed to initialize the hyperplane.

    output_size : int (Default: None)
        The output dimension of the random projection.

    Example:
    --------
    from evidence_model.hrp import HashedRandomProjection
    import torch
    NUM_FEATURES=512
    hrproj = HashedRandomProjection(output_size=1024, random_state=42)
    hrproj.build(input_shape=(NUM_FEATURES,))
    x = tf.random.normal(shape=(2, NUM_FEATURES))
    y = hrproj(x)
    """
    def __init__(self,
                 hyperplane: torch.Tensor = None,
                 random_state: int = 42,
                 input_size: int = None,
                 output_size: int = None,
                 **kwargs):
        super(HashedRandomProjection, self).__init__(**kwargs)
        # check input arguments
        if hyperplane is None:
            if (input_size is None) or (output_size is None):
                raise ValueError(
                    "If hyperplane is None, then input_size and output_size"
                    " must be specified.")
            if random_state is None:
                raise ValueError(
                    "random_state must be specified for "
                    "reproducibility purposes.")
        # initialize new random projection hyperplane
        if hyperplane is None:
            self.hyperplane = torch.nn.parameter.Parameter(
                torch.empty((input_size, output_size)),
                requires_grad=False)
            torch.manual_seed(random_state)
            torch.nn.init.normal_(
                self.hyperplane, mean=0.0, std=1.0)
        else:  # use existing hyperplane
            self.hyperplane = torch.nn.parameter.Parameter(
                hyperplane if torch.is_tensor(hyperplane)
                else torch.tensor(hyperplane),
                requires_grad=False)

    def forward(self, inputs: torch.Tensor):
        projection = torch.matmul(inputs, self.hyperplane)
        hashvalues = torch.heaviside(projection, torch.tensor(0.0))  # int
        return hashvalues

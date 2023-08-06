import logging
import torch
import torch.multiprocessing as mp
import queue
from typing import Dict
import numpy as np

# start logger
logger = logging.getLogger(__name__)


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

    def start_pool(self) -> Dict[str, object]:
        """ GPU Only! Start multiprocessing pool.

            model_hrp = HashedRandomProjection(...)
            pool = model_hrp.start_pool()
            ...
        """
        if torch.cuda.is_available():
            gpu_devices = [
                f"cuda:{i}" for i in range(torch.cuda.device_count())]
            logger.info(f"Using GPU devices: {gpu_devices}")
        else:
            raise ValueError("GPU is required for multiprocessing.")
        # create queues
        ctx = mp.get_context('spawn')
        input_queue = ctx.Queue()
        output_queue = ctx.Queue()
        processes = []
        # loop over each GPU device to create a process
        for device in gpu_devices:
            proc = ctx.Process(
                target=HashedRandomProjection._mb_worker,
                args=(device, self, input_queue, output_queue), daemon=True)
            proc.start()
            processes.append(proc)
        # done and return pool information
        return {
            'input': input_queue,
            'output': output_queue,
            'processes': processes}

    @staticmethod
    def stop_pool(pool: Dict[str, object]):
        """ GPU Only! Stop multiprocessing pool"""
        for proc in pool['processes']:
            proc.terminate()
        for proc in pool['processes']:
            proc.join()
            proc.close()
        pool['input'].close()
        pool['output'].close()

    def infer(self,
              inputs: torch.Tensor,
              pool: Dict[str, object],
              chunk_size: int = None):
        """ GPU Only! Process inputs in chunks using multiprocessing.
            model_hrp = HashedRandomProjection(...)
            pool = model_hrp.start_pool()
            hashed = model_hrp.infer(inputs, pool, chunk_size=32)
            model_hrp.stop_pool(pool)
            torch.cuda.empty_cache()
        """
        # set chunk size
        if chunk_size is None:
            chunk_size = max(
                1, inputs.shape[0] // len(pool["processes"]) // 10)
        if chunk_size < 1:
            raise ValueError("chunk_size must be larger than 0.")
        else:
            logger.info(f"Chunk size: {chunk_size}")
        # send chunks to input queue
        num_chunks = inputs.shape[0] // chunk_size
        num_chunks += int((inputs.shape[0] % chunk_size) != 0)
        input_queue = pool['input']
        for chunk_id in range(num_chunks):
            input_queue.put([
                chunk_id,
                inputs[chunk_id * chunk_size:(chunk_id + 1) * chunk_size, :]
            ])
        # get results from output queue
        output_queue = pool['output']
        results_list = sorted([
            output_queue.get() for _ in range(num_chunks)],
            key=lambda x: x[0])  # sort by chunk_id
        # move results to CPU
        hashvalues = np.concatenate([result[1] for result in results_list])
        return hashvalues

    @staticmethod
    def _mb_worker(device: str, model, input_queue, results_queue):
        """ GPU Only! Worker function for processing a chunk."""
        while True:
            try:
                chunk_id, inputs = input_queue.get()
                model.to(device)
                hashvalues = model(inputs.to(device))
                results_queue.put([
                    chunk_id, hashvalues.detach().cpu().numpy()])  # to RAM
                torch.cuda.empty_cache()  # free GPU memory
            except queue.Empty:
                break

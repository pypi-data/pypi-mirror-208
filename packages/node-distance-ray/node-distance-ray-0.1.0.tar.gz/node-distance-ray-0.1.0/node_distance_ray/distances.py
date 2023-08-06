import node_distance as nd
import logging
import ray
import gc
import os
import psutil


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s: %(message)s",
    datefmt="%y-%m-%d %H:%M:%S"
)

PCT_CPU = float(os.environ.get("NDIST_PCT_CPU", "0.9"))
NUM_CPU = os.environ.get("NDIST_NUM_CPU")
if NUM_CPU is None:
    NUM_CPU = max(1, int(psutil.cpu_count(logical=False) * PCT_CPU))
ray.init(num_cpus=NUM_CPU)


@ray.remote
def node_token_distances_wrapper(*args, **kwargs):
    return nd.node_token_distances(*args, **kwargs)


def node_token_distances(batch_all_edges, batch_num_nodes, cutoff=25):
    try:
        return ray.get([
            node_token_distances_wrapper.remote(all_edges, num_nodes, cutoff)
            for all_edges, num_nodes in zip(batch_all_edges, batch_num_nodes)
        ])
    except Exception as e:
        logger.error(e)
        ray.shutdown()
        gc.collect()

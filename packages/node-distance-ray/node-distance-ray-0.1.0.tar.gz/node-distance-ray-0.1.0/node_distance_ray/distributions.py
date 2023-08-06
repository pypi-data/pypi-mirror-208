import node_distance as nd
import logging
import ray
import gc


logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(name)s: %(message)s",
    datefmt="%y-%m-%d %H:%M:%S"
)


@ray.remote
def nodedist_distribution_wrapper(*args, **kwargs):
    return nd.nodedist_distribution(*args, **kwargs)


def nodedist_distribution(batch_nodedist, xmin=1, xmax=None):
    try:
        return ray.get([
            nodedist_distribution_wrapper.remote(nodedist, xmin, xmax)
            for nodedist in batch_nodedist
        ])
    except Exception as e:
        logger.error(e)
        ray.shutdown()
        gc.collect()


@ray.remote
def tokenvsnode_distribution_wrapper(*args, **kwargs):
    return nd.tokenvsnode_distribution(*args, **kwargs)


def tokenvsnode_distribution(batch_tokendist,
                             batch_nodedist,
                             xmin=None, xmax=None):
    try:
        return ray.get([
            tokenvsnode_distribution_wrapper.remote(
                tokendist, nodedist, xmin, xmax)
            for tokendist, nodedist in zip(batch_tokendist, batch_nodedist)
        ])
    except Exception as e:
        logger.error(e)
        ray.shutdown()
        gc.collect()

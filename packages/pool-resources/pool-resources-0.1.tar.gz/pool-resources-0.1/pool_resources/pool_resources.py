from typing import List, TypeVar, Callable, Sequence, Dict, Tuple
from threading import Lock, Thread
from queue import Queue
from tqdm import tqdm
import traceback
import time

from .resource import Resource
from .logger import logger

T1 = TypeVar("T1")
T2 = TypeVar("T2")


class PoolResources:
    def __init__(
        self, resources: List[Resource], timeout: float = 0, pbar: bool = False
    ):
        self.resources = resources
        self.timeout = timeout
        self.pbar = pbar
        logger.debug(str(self))

    def map(self, fn: Callable[[T1], T2], seq: Sequence[T1]) -> Sequence[T2]:
        if isinstance(seq, zip):
            seq = list(seq)
        logger.debug(f"Got {len(seq)} batch items to be computed")

        if len(self.resources) == 0:
            _range = seq if not self.pbar else tqdm(seq)
            return list(map(fn, _range))
        else:
            return self.map_parallel(fn, seq)

    def _setup_resources_queue(self) -> Queue:
        available_resources = Queue()
        for resource in self.resources:
            available_resources.put(resource)
        return available_resources

    def _setup_unfinished_queue(self, seq: Sequence[T1]) -> Queue:
        unfinished = Queue()
        for i, item in enumerate(seq):
            unfinished.put([i, item])
        return unfinished

    def map_parallel(self, fn: Callable[[T1], T2], seq: Sequence[T1]) -> Sequence[T2]:
        resource_to_thread: Dict[Resource, Thread] = {}
        results: Dict[int, T2] = {}
        results_mutex = Lock()
        available_resources: Queue[Resource] = self._setup_resources_queue()
        unfinished: Queue[Tuple[int, T1]] = self._setup_unfinished_queue(seq)
        pbar = tqdm(total=len(seq)) if self.pbar else None

        while len(results) != len(seq):
            if available_resources.qsize() == 0:
                logger.debug2(
                    f"Queue empty. All devices are processing. Timeout for {self.timeout} seconds."
                )
                time.sleep(self.timeout)
                continue

            resource: Resource = available_resources.get()
            if resource in resource_to_thread:
                resource_to_thread.pop(resource).join()
                pbar.update() if self.pbar else None

            if unfinished.qsize() == 0:
                available_resources.put(resource)
                logger.debug2(
                    f"Empty item list. All are processing or are done. Timeout for {self.timeout} seconds."
                )
                time.sleep(self.timeout)
                continue

            ix, item = unfinished.get()
            thread_args = (
                item,
                fn,
                resource,
                ix,
                available_resources,
                unfinished,
                results,
                results_mutex,
            )
            thread = Thread(target=PoolResources.run_item, args=thread_args)
            resource_to_thread[resource] = thread
            thread.start()
        results = [v for _, v in sorted(results.items(), key=lambda item: item[0])]
        return results

    @staticmethod
    def run_item(
        item: T1,
        fn: Callable[[T1], T2],
        resource: Resource,
        item_index: int,
        available_resources: Queue,
        unfinished: Queue,
        results: Dict[int, T2],
        results_mutex: Lock,
    ):
        """The main running function"""

        # Put the item on the given resource
        item = resource.enable(item)
        try:
            # run the function on the resource enabled item, and, if succeeded, take the result off the resource
            result = fn(item)
            result = resource.disable(result)
            # store the result in the global results dicitonary at the allocated index
            with results_mutex:
                results[item_index] = result
        # If a ValueError is thrown in the function, then it means that the function did not end succesfully. We'll
        #  consider that we should not try to run it again
        except ValueError as e:
            # Except if 'signal' is in there, meaing a worse error happened
            if str(e).find("signal") == -1:
                raise Exception(e)
        # For any other generic exceptions (inlcuding AssertionError), we'll try to run the item again, but also
        #  log the exception so we know the reason it failed, as well as on what resource and item.
        except Exception as e:
            unfinished.put([item_index, item])
            logger.debug(
                f"[resource:{resource}] Error for '{item}'. Exception: {str(e)}"
            )
            str_exception = (
                f"device: {resource}. item: {item}. Exception: {str(e)}."
                f" Backtrace: {traceback.format_exc()}\n"
            )
            open(f"exception.txt", "a").write(str_exception)

        item = resource.disable(item)
        available_resources.put(resource)

    def __str__(self):
        f_str = "Pool Resources."
        f_str += f" Num resources: {len(self.resources)}."
        f_str += (
            f" First resource type: {type(self.resources[0])}"
            if len(self.resources) > 0
            else ""
        )
        f_str += f" Timeout: {self.timeout}s"
        f_str += f" Pbar: {self.pbar}"
        return f_str

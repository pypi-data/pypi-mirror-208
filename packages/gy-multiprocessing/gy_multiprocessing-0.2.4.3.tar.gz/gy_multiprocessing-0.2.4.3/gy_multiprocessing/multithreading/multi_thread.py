from multiprocessing import Pool, cpu_count
from multiprocessing.pool import Pool as PoolType
from types import FunctionType, MethodType
import warnings


class MultiThread:
    def __init__(self, max_threads: int = cpu_count() - 1):
        """
        Args:
            max_threads (int, optional): the maximum number of threads, default is max CPU core - 1

        Using Pool method from multiprocessing to process the multithreading tasks
        """

        # error handling
        if type(max_threads) is not int:
            raise TypeError(f"Wrong type of max_threads '{max_threads}', must be an integer!")
        if max_threads == 0:
            raise IndexError("max threads are set to be 0!")
        if max_threads > cpu_count():
            raise IndexError(
                f"max threads are set to be larger than your cpu cores number! Available cores: {cpu_count()}")
        if max_threads == cpu_count():
            warnings.warn("max threads are set to your cpu cores number! It is not recommended to do that!")

        self.max_threads: int = max_threads

        self.mt_pool: PoolType = Pool(processes=self.max_threads)
        self.mt_pool_list: list = []

    def add(self, func, args: tuple):
        """
        Args:
            func: the function to be called for multi threading
            args (tuple): the arguments of the function

        Adding a task into the multi threading pool
        """

        # TODO! func: FunctionType in PyCharm will warns:
        # TODO! Expected type 'FunctionType', got '(a_string: Any) -> None' instead

        # error handling
        if not isinstance(func, FunctionType) and not isinstance(func, MethodType):
            raise TypeError("Wrong type of func, must be a FunctionType!")
        if not isinstance(args, tuple):
            raise TypeError("Wrong type of args, must be a tuple!")

        self.mt_pool_list.append(self.mt_pool.apply_async(func, args))

    def run(self) -> list:
        """
        Returns:
            the result list of returned value from each tasks

        Running tasks in the pool list
        """

        self.mt_pool.close()
        self.mt_pool.join()

        return_from_pool_list: list = [res.get() for res in self.mt_pool_list]
        return return_from_pool_list

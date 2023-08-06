# gy-multiprocessing

## Installation

### via Github

```bash
pip install git+https://github.com/guangyu-he/gy-multiprocessing
```

### via PyPI

```bash
pip install gy-multiprocessing
```

## Usage

- initializing multiprocessing/multithreading instance
- adding your tasks into the pool, either using loop or sentences
- running the instance

## Note:

- the multiprocessing must work in a function or entrance, do not use it barely in the script
- make sure the code does require multiprocessing/multithreading, wrongly using the multiprocessing may even lose
  performance
- please attention to the queue implementation when using multiprocessing, details check the example below

## Examples

### Multi Processing

```python
import time
import gy_multiprocessing as gymp


def your_func(a_string: int, queue):
    # NOTE! you MUST add an argument for queue and use put() method to fetch the returning value

    print(a_string)
    if a_string % 5 == 0:
        time.sleep(2)

    # NOTE! if you are missing this method, there will be None result returned for current process
    queue.put(a_string)


if __name__ == '__main__':
    # the multiprocessing must work in a function or entrance
    # do not use it barely

    """
    # initializing the multiprocessing instance
    # the default max_process are your cpu max cores
    # max_process could be infinite, but performance will get suffered when the hardware is overloaded
    """
    mp = gymp.MultiProcess(max_process=8)

    # example for multiprocessing in the loop
    outer_loop_times = 5
    for current_loop_index in range(outer_loop_times):
        # your running arguments, must be tuple
        args = (current_loop_index,)

        """
        # adding tasks in multiprocessing pool
        """
        mp.add(your_func, args)

    # it is also possible to add task outside the loop
    mp.add(your_func, (10,))

    """
    # running tasks in multiprocessing pool (returned values are optional)
    """
    result = mp.run()
    print(result)
```

### Multi Threads

```python
import gy_multiprocessing as gymp
import time


def your_func(a_string):
    # your single task function

    print(a_string)
    return a_string + "!"


if __name__ == '__main__':
    # the multithreading must work in a function or entrance
    # do not use it barely

    # timing (optional)
    start = time.time()

    """
    # initializing the multithreading instance
    # the default max_threads are your cpu max cores number - 1
    # max_threads can not larger than your cpu max core number
    """
    mt = gymp.MultiThread(max_threads=4)

    # example for multithreading in the loop
    outer_loop_times = 5
    for current_loop_index in range(outer_loop_times):
        args = (str(current_loop_index),)

        """
        # adding tasks in multi threading pool
        """
        mt.add(your_func, args)

    # it is also possible to work without loop
    args = (str(1),)
    mt.add(your_func, args)
    args = (str(2),)
    mt.add(your_func, args)

    """
    # running tasks in multithreading pool (returned values are optional)
    """
    results = mt.run()
    print(results)

    # timing (optional)
    end = time.time() - start
    print("done in {}s".format("%.2f" % end))
```

### Combined Structure

<b>Note: you can not use multiprocessing or sub-multithreading in the multithreading method</b>

If you want to use such structure, based on your needs, considering using sub-multiprocessing or multithreading in
multiprocessing structure.

```python
import gy_multiprocessing as gymp


def your_sub_func(b_string: int, queue=None):
    # your function that needs to multithreading/multiprocessing

    b_string += 1
    if queue is not None:
        queue.put(b_string)
    return b_string


def your_mt_func(a_string: int, queue):
    # multithreading in multiprocessing structure

    mt = gymp.MultiThread()
    for current_loop_index in range(a_string):
        # your running arguments, must be tuple
        args = (current_loop_index,)
        mt.add(your_sub_func, args)
    result = mt.run()

    # Do not forget queue!
    queue.put(result)


def your_mp_func(a_string: int, queue):
    # sub-multiprocessing in multiprocessing structure

    smp = gymp.MultiProcess()
    for current_loop_index in range(a_string):
        # your running arguments, must be tuple
        args = (current_loop_index,)
        smp.add(your_sub_func, args)
    result = smp.run()

    # Do not forget queue!
    queue.put(result)


if __name__ == '__main__':

    mp = gymp.MultiProcess()

    outer_loop_times = 10
    for current_loop_index in range(outer_loop_times):
        args = (current_loop_index,)
        mp.add(your_mt_func, args)
    print(mp.run())

    print("\n-----”\n")

    mp = gymp.MultiProcess()

    for current_loop_index in range(outer_loop_times):
        args = (current_loop_index,)
        mp.add(your_mp_func, args)
    print(mp.run())
```

## Updates Log

### v0.2.3

#### bug fix

- fixed an issue casing not adding new process to pool until all processed are done in current pool

### v0.2.4

#### feature

- a silent mode is added to multiprocessing which is possible not showing messages in console
- solved multiprocessing not going to the end when there are internal error exceptions in input function
- solved multiprocessing not going to the end when there are missing queue.put() method in input function

### v0.2.4.1 & v0.2.4.2

#### bug fix

- fixed an issue from readme long desc causing installation error

#### improvement

- simplified duplicated codes

### v0.2.4.3

#### updates

- package import improvement. **PLEASE UPDATE IMPORT AS EXAMPLES ABOVE**
- check a boolean type input argument

## Support

feel free to check source code in <a href="https://github.com/guangyu-he/gy-multiprocessing">GitHub</a>, you are welcome
to leave any comments.

2022&copy;Guangyu He, for further support please contact author. <br>
Email: <a href="mailto:me@heguangyu.net">me@heguangyu.net</a>

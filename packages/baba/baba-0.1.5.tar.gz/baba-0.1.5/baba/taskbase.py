import datetime
import logging
import os
from functools import wraps
from types import FunctionType

class TaskBase:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for attr, value in cls.__dict__.items():
            if type(value) is FunctionType:
                setattr(cls, attr, cls.log_execution_time(value))

    @staticmethod
    def log_execution_time(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            str_args = ', '.join(str(arg)[:16] for arg in args[1:])  # args[0] is self
            str_kwargs = ', '.join(f'{k}={v}'[:16] for k, v in kwargs.items())
            params = ', '.join([str_args, str_kwargs]).strip(', ')
            
            start_time = datetime.datetime.now()
            start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')

            result = None  # initialize result variable
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                error_time_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                TaskBase._log(f"{error_time_str}\t{func.__qualname__}({params})出现异常:\t {str(e)}")
                # uncomment the following line if you want the error to be raised after being logged
                # raise

            end_time = datetime.datetime.now()
            time_taken = (end_time - start_time).total_seconds()
            time_taken_str = f"{time_taken:.3f}s"
            log_message = f"{start_time_str}\t{time_taken_str}\t{args[0].__class__.__base__.__name__}.{func.__qualname__}({params})"
            TaskBase._log(log_message)

            return result
        return wrapper

    @staticmethod
    def _log(message):
        # Create a log directory if not exists
        if not os.path.exists('./log'):
            os.makedirs('./log')

        logging.basicConfig(filename='./log/execution.log', level=logging.INFO, format='%(message)s',encoding='utf-8')
        logging.info(message)
        print(message)

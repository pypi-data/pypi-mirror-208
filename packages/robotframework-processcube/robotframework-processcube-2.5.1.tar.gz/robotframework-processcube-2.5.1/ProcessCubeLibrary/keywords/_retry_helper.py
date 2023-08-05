import functools
import time

from requests.exceptions import ConnectionError

from robot.api import logger

def retry_on_exception(func):
    
    @functools.wraps(func)
    def retry_helper(self, *args, **kwargs):
        current_retry = 0

        local_kwargs = kwargs.copy()

        current_delay = local_kwargs.get('delay', self._delay)
        backoff_factor = local_kwargs.get('backoff_factor', self._backoff_factor)
        max_retries = local_kwargs.get('max_retries', self._max_retries)

        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in local_kwargs.items()]
    
        signature = ", ".join(args_repr + kwargs_repr)
    
        logger.debug(f"Calling retry for {func.__name__}({signature})")

        logger.debug(f"_max_retries: {max_retries}")
        logger.debug(f"_backoff_factor: {backoff_factor}")
        logger.debug(f"_delay: {current_delay}")
        

        # delete the max_retries, delay and backoff_factor from the kwargs
        if 'max_retries' in local_kwargs:
            #del local_kwargs['max_retries']
            pass

        if 'delay' in local_kwargs:
            #del local_kwargs['delay']
            pass

        if 'backoff_factor' in local_kwargs:
            #del local_kwargs['backoff_factor']
            pass

        while True:
            try:
                value = func(self, *args, **local_kwargs)
    
                logger.debug(f"{func.__name__!r} returned {value!r}")
            
                return value
                
            except ConnectionError as e:
                time.sleep(current_delay)
                current_retry = current_retry + 1
                current_delay = current_delay * backoff_factor
                
                if current_retry > max_retries:
                    raise Exception(f"Calling {func.__name__} with max_retries {max_retries} without success.") from e

                logger.info(f"[{func.__name__}] Retry count: {current_retry} of {max_retries}; delay: {current_delay} and backoff_factor: {backoff_factor}")

    return retry_helper

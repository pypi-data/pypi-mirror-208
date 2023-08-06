import logging
import time
from logstash_async.handler import AsynchronousLogstashHandler
from logstash_async.formatter import LogstashFormatter
import traceback


logger = logging.getLogger("")


def init_logger(config):
    global logger
    logger = logging.getLogger(config["name"])
    logger.setLevel(logging.INFO)
    logstash_formatter = LogstashFormatter(message_type=f"egune-{config['name']}")
    logstash_handler = AsynchronousLogstashHandler(config["host"], config["port"], None)
    logstash_handler.setFormatter(logstash_formatter)
    logger.addHandler(logstash_handler)
    logger.info(f"Started {config['name']}", extra={"log_event": "system started"})


def log_request(request_name, input_prep=None, output_prep=None):
    def ultra_wrapped(func):
        def wrapped(data):
            s = time.time()
            original_input = data
            try:
                if input_prep is not None:
                    data = input_prep(data)
                if isinstance(data, tuple):
                    result = func(*data)
                else:
                    result = func(data)
                if output_prep is not None:
                    result = output_prep(result)
                logger.info(
                    "Processed",
                    extra={
                        "app": original_input.get("app_id", None),
                        "log_event": request_name,
                        "process_input": str(original_input),
                        "process_output": str(result),
                        "time": time.time() - s,
                    },
                )
                return result
            except Exception as e:
                logger.error(
                    "Failed",
                    extra={
                        "app": original_input.get("app_id", None),
                        "log_event": request_name + ":Failed",
                        "process_input": str(original_input),
                        "process_output": str(traceback.format_exc()),
                        "time": time.time() - s,
                    },
                )
                raise e

        return wrapped

    return ultra_wrapped


def log(extra):
    logger.info("custom", extra=extra)

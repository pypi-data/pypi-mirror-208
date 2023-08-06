import os
import sys
import queue
import logging

from logging.handlers import TimedRotatingFileHandler
from logging.handlers import QueueHandler, QueueListener

from .logger_pg_handler import PGHandler

FORMATTER = logging.Formatter("[%(asctime)s] [%(name)s.%(funcName)s:%(lineno)d] [%(levelname)s]: %(message)s")
LOG_FILE = ".citros/citros.log"
# create DIR if not exists
if not os.path.isdir(".citros"):
   os.makedirs(".citros")

# log to console
def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   # console_handler.setLevel(logging.ERROR)
   console_handler.setFormatter(FORMATTER)
   return console_handler

# log to file
def get_file_handler():
   file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')   
   file_handler.setFormatter(FORMATTER)
   return file_handler

# log to postgres
def get_gql_handler(sync_logs, batch_run_id, simulation_run_id):
   gql_handler = PGHandler(sync_logs, batch_run_id, simulation_run_id)
   FORMATTER = logging.Formatter("%(message)s")
   gql_handler.setFormatter(FORMATTER)   
   return gql_handler

# def get_logger(logger_name, citros):
#    # print(f"****** get_logger {logger_name}")
#    log_queue = queue.Queue(-1)
#    queue_handler = QueueHandler(log_queue)
   
#    logger = logging.getLogger(logger_name)
#    logger.setLevel(logging.DEBUG)
#    logger.addHandler(queue_handler)
   
#    listener = QueueListener(log_queue, 
#                               # get_console_handler(), 
#                               get_file_handler(), 
#                               get_gql_handler(citros),
#                               respect_handler_level=True
#                            )
#    listener.start()
#    # logger.propagate = False
#    return logger, listener
   
loggers = {}
def get_logger(logger_name, sync_func, batch_run_id=None, simulation_run_id=None):
   logger_name = f"{logger_name}-{batch_run_id}-{simulation_run_id}"
   # print(f"****** get_logger {logger_name}", loggers)
   if loggers.get(logger_name, None):      
      loggers[logger_name]["listener"].start()      
      return loggers[logger_name]["logger"], loggers[logger_name]["listener"]
   else:
      loggers[logger_name] = {}
   
   log_queue = queue.Queue(-1)
   queue_handler = QueueHandler(log_queue)
   
   loggers[logger_name]["logger"] = logging.getLogger(logger_name)
   loggers[logger_name]["logger"].setLevel(logging.DEBUG)   
   loggers[logger_name]["logger"].addHandler(queue_handler)
   
   loggers[logger_name]["listener"] = QueueListener(log_queue, 
                                                    get_console_handler(), 
                                                    get_file_handler(), 
                                                    get_gql_handler(sync_func, batch_run_id, simulation_run_id),
                                                    respect_handler_level=True
                                                )      
   loggers[logger_name]["listener"].start()   
   
#    loggers[logger_name]["logger"].propagate = False
   return loggers[logger_name]["logger"], loggers[logger_name]["listener"]

# def stop_logger(logger_name):
#    loggers[logger_name]["listener"].stop()

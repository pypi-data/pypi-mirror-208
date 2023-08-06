import os
import atexit
import logging
import datetime 
import threading
from citros.citros_utils import setInterval
import requests


class PGHandler(logging.Handler):
    """
    A handler which pipes all logs to gql through postgres.
    """
    def __init__(self, sync_func, batch_run_id=None, simulation_run_id=None):
        """
        customToken: The loggly custom token account ID
        appTags: Loggly tags. Can be a tag string or a list of tag strings        
        """
        logging.Handler.__init__(self)
        
        self.batch_run_id = batch_run_id
        self.simulation_run_id = simulation_run_id
        self.sync_func = sync_func
        self.pid = os.getpid()                                    

        self.timer = None
        self.logs = []
        self.timer = self._flushAndRepeatTimer()
        atexit.register(self._stopFlushTimer)
           
    @setInterval(5)
    def _flushAndRepeatTimer(self):
        self.flush()

    def _stopFlushTimer(self):
        self.timer.set()
        self.flush()
    
    def _prepData(self, record):
        # payload = {}
        d = record.__dict__
        data = {
            k: v for (k, v) in d.items()            
        }
        # print("data: ", data)
        return {
            "process_id": int(data["process"]),
            "batch_run_id": self.batch_run_id,
            "sid": self.simulation_run_id,
            "process_name": data["processName"],
            "logger_name": data["name"],
            "path_name": data["pathname"],
            "module": data["module"],
            "file_name": data["filename"],
            "function_name": data["funcName"],
            "line_number": data["lineno"],
            "log_level": data["levelname"],
            "log_level_number": data["levelno"],
            "message": self.format(record),
            "exc_info": data["exc_info"],
            "thread_id": data["thread"],
            "thread_name": data["threadName"],
            "created": datetime.datetime.strptime(data["asctime"],"%Y-%m-%d %H:%M:%S,%f").isoformat()  
        }
    
    def flush(self, current_batch=None):   
        if current_batch is None:
            self.logs, current_batch = [], self.logs
        
        if len(current_batch)== 0:
            return
        
        request_json = {
            "logs": current_batch
        }
          
        resp = self.sync_func(request_json)   
        if not resp:
            # retry on fail.
            self.logs = current_batch + self.logs            
                    
    def emit(self, record):
        """
        Override emit() method in handler parent for sending log to Postgres
        API
        """        
        
        pid = os.getpid()
        if pid != self.pid:
            self.pid = pid
            self.logs = []
            self.timer = self._flushAndRepeatTimer()
            atexit.register(self._stopFlushTimer)

        # avoid infinite recursion
        if record.name.startswith('requests'):
            return
                
        self.logs.append(self._prepData(record))
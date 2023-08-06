class citros_utils():
    def __init__(self, citros):
        self.citros = citros      
        self.log = citros.log
                        
    def get_launch(self, batch_run_id):        
        query = """
        query getData($batchRunId: UUID!) {
            batchRun(id: $batchRunId) {                                
                id                
                simulation {
                    id                    
                    launch {
                        id
                        name
                        package {
                            id
                            name
                        }
                    }
                }                
            }
        }
        """        
        result = self.citros.gql_execute(query, variable_values={"batchRunId": batch_run_id})
        return result
        
   
import threading

def setInterval(interval):
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop():  # executed in another thread
                while not stopped.wait(interval):  # until stopped
                    function(*args, **kwargs)

            t = threading.Thread(target=loop)
            t.daemon = True  # stop if the program exits
            t.start()
            return stopped
        return wrapper
    return decorator

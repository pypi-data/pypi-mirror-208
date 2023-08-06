from collections.abc import MutableMapping
from decouple import config
from pathlib import Path
import traceback
import datetime 
import json
import yaml
import os

# from .rosbag import BagReader
from .rosbag import BagReaderSQL

###########################
#           BAGd
###########################  
class citros_bag():
    def __init__(self, citros):     
        self.citros = citros
        self.log = citros.log 
        
        self.BUCKET = 'citros_bags'
        self.CITROS_BAG_TOKEN = f"{citros.CITROS_DOMAIN}/api/bag/token"  
        
        self.CITROS_DATA_HOST = config("CITROS_DATA_HOST", None)
        self.CITROS_DATA_PORT = config("CITROS_DATA_PORT", "5432")
        self.CITROS_DATA_DATABASE = config("CITROS_DATA_DATABASE", "postgres")
        self.CITROS_DATA_USERNAME = config("CITROS_DATA_USERNAME", "citros_anonymous")
        self.CITROS_DATA_PASSWORD = config("CITROS_DATA_PASSWORD", "citros_anonymous")
        
        self.CONFIG_FOLDER = config("CONFIG_FOLDER", 'tmp/config')
        # if not self.CITROS_DATA_HOST:
        #     raise Exception("env variable CITROS_DATA_HOST is None, the simulation will not be able to upload the data to DB.")            
    
    # get token to upload the bag to GCP bucket.
    def get_bag_access_token(self):
        if not self.citros.isAuthenticated():
            self.log.error("User is not logged in. please log in first.")
            return None
        
        rest_data = None
        import requests      
        try:
            resp = requests.post(self.CITROS_BAG_TOKEN, headers={
                "Authorization": f"Bearer {self.citros._get_token()}"
            })
            if resp.status_code == 404:      
                self.log.error("cant find [{self.CITROS_BAG_TOKEN}] url.")
                return 
            rest_data = resp.json()
        except Exception as err:
            self.log.error("Cant get access token at this moment... check google json file that may is currapt (sa-api-secret)")
            self.log.error(err)
            return    
                                
        try:
            # token = rest_data
            token = rest_data["access_token"]            
            expires_in = rest_data["expires_in"]
            token_type = rest_data["token_type"]
        except KeyError as err:
            return None
        return token
    
    def emit(self, path_to_bag, batch_run_id, simulation_run_id, option='google'):       
        my_file = Path(path_to_bag)
        if not my_file.is_file():
            self.log.error(f"Bag file {path_to_bag} doesn't exists.")
            return False, f"Bag file {path_to_bag} doesn't exists.", None
                    
        path_to_metadata = "/".join(path_to_bag.split("/")[:-1]) +"/metadata.yaml"           
        if option == 'google':
            return self.sync_bag_google_bucket(batch_run_id, simulation_run_id, path_to_metadata, path_to_bag)      
        
        # TODO: if  bag is 3db -> sqlite
        # TODO: if  bag is mcap -> mcap
        # TODO: log in between!
        # TODO: fix event logs for ros... after bad is not done! 
        return self.sync_bag_pgdb(batch_run_id, simulation_run_id, path_to_metadata, path_to_bag)
    
    ################################################################################################
    ### sync BAG to Postgres DB
    ################################################################################################
    def sync_bag_pgdb(self, batch_run_id, simulation_run_id, path_to_metadata, path_to_bag):        
        import psycopg2
        self.log.debug("------------------------------------------------------------------------------------")
        self.log.debug(f"uploading bag to PGDB")
        
        connection = None
        # get data-token from citros to access data DB.             
        user = self.citros.getUser()      
        
        if user is None or user["username"] is None or user["id"] is None:
            error_text = f"Error at sync_bag, failed to get user from CITROS."
            self.log.error(error_text)                                 
            return False, error_text, None
        
        if not self.CITROS_DATA_HOST:
            raise Exception(f"[{datetime.datetime.now()}] ENV variable [CITROS_DATA_HOST] is None, the simulation will not be able to upload the data to DB.")            
        
        connection = psycopg2.connect(user=user["username"],
                                    password=user["id"],
                                    host=self.CITROS_DATA_HOST,
                                    port=self.CITROS_DATA_PORT,
                                    database=self.CITROS_DATA_DATABASE)
        cursor = connection.cursor()
        postgres_insert_query = f""" 
            insert into data_bucket."{batch_run_id}"
            (sid, rid, time, topic, type, data)
            values (%(sid)s, %(rid)s, %(time)s, %(topic)s, %(type)s, %(data)s);
        """
        
        try:                                       
            #####################
            # Uploads configs    
            #####################
            import glob
            rid_counter = 0
            self.log.debug(f"uploading config")
            for config_file in glob.glob(self.CONFIG_FOLDER + "/*"):                
                with open(f"{config_file}", 'r') as file:                                                     
                    config_dict = yaml.load(file, Loader=yaml.FullLoader) 
                    self.log.debug(f"uploading config [{config_file}]")
                    
                    record_to_insert = {
                        "sid": simulation_run_id,
                        "rid": rid_counter,
                        "time": 0,
                        "topic": '/config',
                        "type": 'params',
                        # "type": config_file.split('.')[0],
                        "data": json.dumps(config_dict)
                    }
                    rid_counter = rid_counter + 1
                    
                    cursor.execute(postgres_insert_query, record_to_insert)                                                        
                    connection.commit()                
                      
            
            #####################
            # Uploads metadata
            #####################
            self.log.debug(f" + uploading metadata")
            with open(path_to_metadata, 'r') as file:                                                     
                metadata_dict = yaml.load(file, Loader=yaml.FullLoader) 
                self.log.debug(f" - uploading metadata")
                
                record_to_insert = {
                    "sid": simulation_run_id,
                    "rid": 0,
                    "time": 0,
                    "topic": '/metadata',
                    "type": 'metadata',
                    "data": json.dumps(metadata_dict)
                }
                
                # self.log.debug("metadata record_to_insert:", record_to_insert)
                # record_to_insert = (simulation_run_id, 0, 0, '/metadata', 'metadata', json.dumps(metadata_dict))                
                # self.log.debug(postgres_insert_query, record_to_insert)
                
                cursor.execute(postgres_insert_query, record_to_insert)                                                        
                connection.commit()                                 
            
            #####################
            # Uploading data
            #####################  
            self.log.debug(f" +++ uploading bag to PG")
            bagReader = BagReaderSQL()
            total_size = 0
            for buffer in bagReader.read_messages(path_to_bag, simulation_run_id):
                # self.log.debug(f" + read_messages")
                size = buffer.seek(0, os.SEEK_END)
                size = buffer.tell()
                total_size = total_size + size
                buffer.seek(0)                
                self.log.debug(f" \tinserting buffer size: { (size / 1024 ) / 1024 } MB")
                if size == 0:
                    continue
                cursor.execute(f'SET search_path TO data_bucket')
                try:           
                    cursor.copy_from(buffer, batch_run_id, sep=chr(0x1E), null="", columns=['sid', 'rid', 'time', 'topic', 'type', 'data'])                
                except (Exception, psycopg2.Error) as error:
                    buffer.seek(0)                      
                    self.log.error(f" Failed to insert record into table, aboring uploading to PG DB.", error) 
                    # self.log.error(traceback.format_exc())
                    self.log.exception(error)     
                    # self.log.debug("===============================================================================================")
                    # self.log.debug(buffer.getvalue())
                    # self.log.debug("===============================================================================================")
                    return False, "got exception from pgdb", str(error)
                # buffer.truncate(0)
                # buffer.seek(0)
                # buffer.close()
                connection.commit()
            self.log.debug(f" --- done uploading to PG")
            return True, f"success, uploaded [{path_to_metadata}],[{path_to_bag}] to Postgres. [size: {(total_size / 1024)/1024} MB]", None
        except (Exception, psycopg2.Error) as error:
            self.log.exception(f" Failed to insert record into table, aboring uploading to PG DB.", error) 
            self.log.exception(traceback.format_exc())
            return False, "got exception from pgdb", str(error)
        finally:
            # closing database connection.
            if connection:
                cursor.close()
                connection.close()
                self.log.debug(f"PostgreSQL connection is closed")  
                
    ################################################################################################
    ### sync BAG to Google Bucket
    ################################################################################################
    def sync_bag_google_bucket(self, batch_run_id, simulation_run_id, path_to_metadata, path_to_bag):
        self.log.debug("------------------------------------------------------------------------------------")
        self.log.debug("uploading bag to google bucket")
        if not self.citros.isAuthenticated():
            self.log.debug("not authenticated. please login first.")
            return False, "not authenticated. please login first." , None       
        
        user = self.citros.getUser()
        tenant =  user["organization"]["domainPrefix"]
        
        bag_file_name = path_to_bag.split('/')[-1]            
        data_url = f'https://storage.googleapis.com/upload/storage/v1/b/{self.BUCKET}/o?uploadType=media&name={tenant + "/" + batch_run_id + "/sid-" + simulation_run_id + "/" + bag_file_name}'        
        
        metadata_name = path_to_metadata.split('/')[-1]  
        metadata_url = f'https://storage.googleapis.com/upload/storage/v1/b/{self.BUCKET}/o?uploadType=media&name={tenant + "/" + batch_run_id + "/sid-" + simulation_run_id + "/" + metadata_name}'        

        google_token = self.get_bag_access_token()
        # self.log.debug("google_token", google_token)
        if google_token is None:
            error_text = f"[ERROR] at sync_bag, failed to get google token from CITROS."
            self.log.error(error_text)                                  
            return False, error_text, None  
        
        import requests  
        # uploading metadata first, assuming much smaller file. 
        with open(path_to_metadata, 'rb') as data:
            # metadata = yaml.safe_load(data)
            metadata_resp = requests.post(metadata_url,
                                data=data,
                                headers={
                                    "Authorization": f"Bearer {google_token}",
                                    "Content-Type" : "application/octet-stream"
                                }
                            ) 
        if metadata_resp.status_code != 200:                        
            error_text = f"[ERROR] from sync_bag: [{metadata_resp.status_code}]:[{metadata_resp.reason}]"
            self.log.error(error_text)
            return False, error_text, None  
        
        self.log.info(f"done updating metadata to: [{batch_run_id}],[{simulation_run_id}] - [{metadata_resp.text}]")
        
        # uploading the bag
        with open(path_to_bag, 'rb') as data:            
            bag_resp = requests.post(data_url,
                                data=data,
                                headers={
                                    "Authorization": f"Bearer {google_token}",
                                    "Content-Type" : "application/octet-stream"
                                }
                            ) 
            # self.log.debug("bag_resp", bag_resp)
            
        if bag_resp.status_code != 200:                        
            error_text = f"[ERROR] from sync_bag: [{bag_resp.status_code}]:[{bag_resp.reason}]"
            self.log.error(error_text)            
            # self.log.debug("sync_bag", CITROS_BAG, request_json)
            return False, error_text, None  
        
        # self.log.debug("resp", json.loads(bag_resp.text))
        
        self.log.info(f"done updating bag to: [{batch_run_id}],[{simulation_run_id}] - [{bag_resp.text}] ")        
        return True, f"success, uploaded [{path_to_metadata}],[{path_to_bag}]", bag_resp.text
    
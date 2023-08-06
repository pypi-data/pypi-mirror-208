import os
import yaml
## ENV
from decouple import config
import traceback
import jwt

## Postgres
# import psycopg2
# from psycopg2 import Error
## graphQL
from gql import Client, gql
from gql.transport.exceptions import TransportQueryError
from gql.transport.requests import RequestsHTTPTransport

from .citros_events import citros_events
from .citros_integration import citros_integration
from .citros_utils import citros_utils
from .citros_batch import citros_batch
from .citros_bag import citros_bag
from .parsers import parser_ros2
from .citros_params import citros_params
from .logger import get_logger

citros = None
class Citros:
    def __init__(self, batch_run_id=None, simulation_run_id=None):    
        # if self.init: # init only once. 
        #     return
        # self.init = True
        
        self.CONFIG_DIR = ".citros"
                    
        self._user = None
        self._jwt_token = None
        
        # GQL
        self._gql_client = None
        
        # for logger
        self.batch_run_id = batch_run_id
        self.simulation_run_id = simulation_run_id    
        
        self.CITROS_DOMAIN = config("CITROS_DOMAIN", "https://citros.io")
        print(f"--- using self.CITROS_DOMAIN = {self.CITROS_DOMAIN}")
        
        self.CITROS_ENTRYPOINT = f"{self.CITROS_DOMAIN}/api/graphql"
        self.CITROS_LOGS = f"{self.CITROS_DOMAIN}/api/logs"        
        self.CITROS_GTOKEN = f"{self.CITROS_DOMAIN}/api/gtoken" 
        self.CITROS_HEALTH_CHECK = f"{self.CITROS_DOMAIN}/api/check" 
        
        
        # TODO: fix this! how to make it beautiful?s
        self.log = None
        self.listener = None
        self.log, self.listener = get_logger(__name__, self.sync_logs, self.batch_run_id, self.simulation_run_id)
        
        # if self.isAuthenticated():
        #     self.getUser()
        
        ########################################################################
        ###     Citros components
        ########################################################################
        self.events = citros_events(self)        
        self.parser_ros2 = parser_ros2(self.log)
        self.integration = citros_integration(self)        
        self.params = citros_params(self)
        self.utils = citros_utils(self)
        self.bag = citros_bag(self)
        self.batch = citros_batch(self)
        
    def close(self):                
        if self.listener:         
            self.listener.stop()    
                    
    def _remove_token(self):
        self._set_token(None)
        
    def _set_token(self, jwt_token):
        #TODO: check token validity
        # print(f"jwt_token [{jwt_token}]")
        if not jwt_token or jwt_token == '':
            self._jwt_token = None
            try:
                os.remove(f"{self.CONFIG_DIR}/auth")
                return
            except FileNotFoundError as e:
                return # its ok that there is no file.                
            except Exception as e:
                self.log.exception(e)       
                traceback.print_exc()
            return    
            
        # create DIR if not exists
        if not os.path.isdir(self.CONFIG_DIR):
            os.makedirs(self.CONFIG_DIR)
            
        try:
            with open(f"{self.CONFIG_DIR}/auth", mode='w') as file:            
                file.write(jwt_token)                  
        except FileNotFoundError as e:
            self.log.exception(e)
            traceback.print_exc()
        except Exception as e:
            self.log.exception(e)
            traceback.print_exc()
        finally:
            self._jwt_token = jwt_token                        
        
        return self._jwt_token
    
    def _get_token(self):
        try:
            if self._jwt_token:
                return self._jwt_token
            
            with open(f"{self.CONFIG_DIR}/auth", mode='r') as file:            
                self._jwt_token = file.read()
        except FileNotFoundError as e:
            # Key file wasn't found. assuming the user is not logged in...
            self._jwt_token = None
            return None
        except Exception as e:
            self.log.exception(e)
            traceback.print_exc()
        
        if self._jwt_token == '':
            print("ERROR: self._jwt_token is empty, removing. ")
            self._remove_token()
        # TODO: check token is valid. if not remove token!
        return self._jwt_token
    
    ###########################
    # Public
    ###########################
    def logout(self):
        """Logs out of CiTROS
        """                
        self._remove_token()
        self._user = None
        
        self.log.debug("logged out.")
    
    def isAuthenticated(self):
        """returns the authentication status

        Returns:
            boolean: True if the user is logged in. 
        """        
        return self._get_token() is not None
    
    def checkStatus(self):
        if not self.isAuthenticated():
            print("User is not logged in. please log in first.")
            return False

        import requests      
        try:
            resp = requests.post(self.CITROS_HEALTH_CHECK, headers={
                "Authorization": f"Bearer {self._get_token()}"
            })                
            if resp.status_code == 200 and resp.text == "OK":
                return True
        except Exception as err:
            print("[ERROR] cant get access token at this moment...")
            print(err)
            return False
        return False
    
    def authenticate_with_key(self, key):
        """Login to CiTROS using a key

        Args:
            key (string): a key generated by CiTROS system.
        """        
        if self.isAuthenticated():
            return 
        
        query = """
            mutation auth($key: AuthenticateKeyInput!){
                authenticateKey(input: $key){
                    results {
                    _role
                    fail
                    message
                    }
                }
            }
            """        
        result = self.gql_execute(query, variable_values={ "key": {"jwtToken": key}})
        
        # print("login result", result)
        if not result["authenticateKey"]["results"][0]["fail"]:
            token = key
        else:
            print("ERROR: failed to log in. resp", result)
            token = None
        
        if token:
            self._set_token(token)
            self.log.info("Authenticated!")            
        else:
            self.log.error(f"ERROR Authenticated! wrong username or password")
            return False
        return True
        
    def login(self, email, password):
        """_summary_

        Args:
            email (string): the user email 
            password (string): the users password
        """                
        if self.isAuthenticated():
            return True
        
        query = """
            mutation AuthenticateUser($email: String!, $password: String!) {
                authenticate(input: {
                    email: $email, 
                    password: $password
                }) {
                    jwt
                }
            }
            """        
        result = self.gql_execute(query, variable_values={
            "email": email,
            "password": password
        })
        # print("login result", result)
        if result:
            token = result["authenticate"]["jwt"]
        else:
            print("ERROR: failed to log in. resp: ", result)
            token = None
            return False
        
        try:
            # bug fix. addede audience as it didnt work in some cases. 
            decoded = jwt.decode(token, options={"verify_signature": False}, audience="postgraphile")        
            # print("decoded: ", decoded)
        except Exception as err:     
            print("ERROR: failed to log in. token: ", token) 
            self.log.exception(err)        
            traceback.print_exc()
            return False
        
        if token and decoded["role"] != "citros_anonymous":
            self._set_token(token)
            self.log.info("Authenticated!")
        else:
            print("ERROR Authenticated! wrong username or password for [{email}]")
            self.log.error(f"ERROR Authenticated! wrong username or password for [{email}]")
            return False
        return True
            
    def getUser(self):
        """returns the currently logged in user with all his data

        Returns:
            user: all user data from CiTROS
        """        
        if self._user:
            return self._user
        query = """
            query getCurrentUser {
                currentUser {  
                    id        
                    username        
                    role{
                        id
                        role
                    }           
                    organization{
                        id 
                        name
                        domainPrefix
                    }                    
                }
            }  
            """
        try:
            result = self.gql_execute(query)            
            self._user = result["currentUser"]    
        except Exception as e:
            self.logout()
            self._user = None
        return self._user
    
    ###########################
    # Docker
    ###########################    
    def get_access_token(self):
        if not self.isAuthenticated():
            print("user is not logged in. please log in first.")
            return 
        
        rest_data = None
        import requests      
        try:
            resp = requests.post(self.CITROS_GTOKEN, headers={
                "Authorization": f"Bearer {self._get_token()}"
            })          
            rest_data = resp.json()
        except Exception as err:
            print("[ERROR] cant get access token at this moment...")
            print(err)
            return    
        
        # print(rest_data)
        
        # token = rest_data["id_token"]
        try:
            # token = rest_data
            token = rest_data["access_token"]            
            expires_in = rest_data["expires_in"]
            token_type = rest_data["token_type"]
        except KeyError as err:
            return None
        return token
            
    ###########################
    # GraphQL
    ###########################             
    def _get_transport(self):                            
        transport = RequestsHTTPTransport(
            url=self.CITROS_ENTRYPOINT,
            verify=True,
            retries=3            
        )     
        # create GQL client for user or for anonymous user. 
        if self.isAuthenticated():
            transport.headers = {
                "Authorization": f"Bearer {self._get_token()}"
            }
        return transport

    def _get_gql_client(self):
        if self._gql_client:
            return self._gql_client
        # https://gql.readthedocs.io/en/v3.0.0a6/intro.html
        transport = self._get_transport()
        self._gql_client = Client(transport=transport, fetch_schema_from_transport=False)
        return self._gql_client
        
    def gql_execute(self, query, variable_values=None):
        """_summary_

        Args:
            query (gql): gql query
            variable_values (dict, optional): variables for the gql query. Defaults to None.

        Returns:
        """
        
        gql_query = gql(query)
        try:
            return self._get_gql_client().execute(gql_query, variable_values=variable_values)
        except TransportQueryError as err:                    
            print("TransportQueryError: Error while querying: query=",query, " variable_values=",variable_values)
            self.log.exception(err) 
            traceback.print_exc()
                 
            if err.errors[0].get('errcode', '') == "23503":                
                self.logout()            
        except Exception as e:    
            print("Exception: Error while querying: query=",query, " variable_values=",variable_values)
            self.log.exception(e)
            traceback.print_exc()
                           
        return None
    
    ###########################
    # CITROS sync
    ###########################
    def sync_logs(self, request_json):
        if not self.isAuthenticated():
            print("User is unauthenticated. please login first!")
            return
        
        import requests     
        try:           
            resp = requests.post(self.CITROS_LOGS, 
                              json=request_json, 
                              headers={"Authorization": f"Bearer {self._get_token()}"}
                            )         
            if resp.status_code != 200:
                print(f"Error from sync_logs: {resp.status_code}: {resp.reason}", resp)
                # print("sync_logs", self.CITROS_LOGS, request_json)
                return False
        except Exception as e:
            print(f"Error from sync_logs: {e}", resp)
            # print("sync_logs", self.CITROS_LOGS, request_json)
            return False
        
        return True
    
        
   
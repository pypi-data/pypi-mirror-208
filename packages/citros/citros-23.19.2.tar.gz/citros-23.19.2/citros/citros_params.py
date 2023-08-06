# from pkg_resources import Distribution
from soupsieve import match
import yaml
import json
from pathlib import Path
from decouple import config

class citros_params():
    def __init__(self, citros):
        self.citros = citros
        self.log = citros.log
        
        self.CONFIG_FOLDER = config("CONFIG_FOLDER", 'tmp/config')
    
    def _get_params(self, batch_run_id, sid=""):
        query = """
        query getParametersFromBatchRun($batchRunId: UUID!, $sid: String!){
            batchRun(id:$batchRunId){
                id                
                simulation {
                project {
                    rosPackagesList {
                        id
                        name
                        rosNodesByPackageIdList {
                        id
                        name
                        rosNodeParametersList {
                            id
                            name
                            value
                            parameterType
                        }
                        }
                    }
                }
                parameterSetup{
                    id
                    name
                    parameterSettingsList {
                            param1
                            param1Type
                            param2
                            param2Type
                            distType
                            id
                            nodeParameterId
                        }          
                    }
                }                
            }
            simulationEventsList(
                condition: {sid: $sid, batchRunId: $batchRunId, event: STARTING, tag: "CONFIG"}
            ) {                
                metadata
            }
        }
        """
        result = self.citros.gql_execute(query, variable_values={"batchRunId": batch_run_id, "sid": sid})        
        return result
   
    def _coercion(self, value, type):
        if type == "FLOAT":
            return float(value)
        if type == "INT":
            return int(float(value))
        return value
        
    def _eval_distribution(self, parameter_setting):
        import numpy as np

        distribution_type = parameter_setting["distType"]
        param1 = parameter_setting["param1"]
        param1Type = parameter_setting["param1Type"]
        param1 = self._coercion(param1, param1Type)
        param2 = parameter_setting["param2"]
        param2Type = parameter_setting["param2Type"]
        param2 = self._coercion(param2, param2Type)
        
        if distribution_type == "NORMAL":                            
            return np.random.normal(param1, param2)
        
        if distribution_type == "EXPONENTIAL":                            
            return np.random.exponential(param1)
        
        if distribution_type == "LAPLACE":                 
            return np.random.laplace(param1, param2)
        
        if distribution_type == "POISSON":                            
            return np.random.poisson(param1)
        
        if distribution_type == "POWER":                            
            return np.random.power(param1)
                
        if distribution_type == "UNIFORM":                 
            return np.random.uniform(param1, param2)
           
        if distribution_type == "ZIPF":                            
            return np.random.zipf(param1)   
        
        if distribution_type == "VONMISES":                 
            return np.random.vonmises(param1, param2)
          
        if distribution_type == "RAYLEIGH":                            
            return np.random.rayleigh(param1)   
        
        if distribution_type == "FLOAT":
            value = self._coercion(param1, param1Type)
            return value
        
        if distribution_type == "STRING":                            
            return param1
              
        self.log.error(f"Error: {distribution_type} is not supported.")        
        
    def get_config(self, batch_run_id, sid=""):
        data = self._get_params(batch_run_id, sid)
        if not data:
            self.log.error("Didnt get any data from GQL.")
            print("Didnt get any data from GQL.")  
            return 
        # self.log.debug(json.dumps(data, indent=4))
        
        # in case sid is provided, and there was already a run with this sid. load original config to run it again.
        reloaded_parameters = None
        if len(data["simulationEventsList"]) > 0:
            reloaded_parameters = data["simulationEventsList"][0]["metadata"]
            self.log.info(f"Reloaded config from allready used [batch_run_id-sid] [{batch_run_id}-{sid}]")  
            # print(f"Reloaded config from allready used [batch_run_id-sid] [{batch_run_id}-{sid}]")
            return reloaded_parameters
            
        if data["batchRun"]["simulation"] is None:
            self.log.error("ERROR! Cant get parameters from CiTROS. There is no simulation attached to batch.")  
            return     
              
        # users parametre setup
        parameter_settings_list = data["batchRun"]["simulation"]["parameterSetup"]["parameterSettingsList"]        
        paramValues = {} 
        for ps in parameter_settings_list:
            try:
                paramValues[str(ps["nodeParameterId"])] = self._eval_distribution(ps)
            except Exception as e:
                self.log.error(f"Error in _eval_distribution, parameter_settings_list: [{json.dumps(ps, indent=4)}]")
                # self.log.excption(e)
                raise e
        
        # load defaults from ros nodes. 
        ros_packages_list = data["batchRun"]["simulation"]["project"]["rosPackagesList"]
        config = {}   
        for package in ros_packages_list:
            config[package["name"]] = {}
            for node in package["rosNodesByPackageIdList"]:                
                config[package["name"]][node["name"]] = {
                    "ros__parameters": {}
                }
                for parameter in node["rosNodeParametersList"]:                    
                    value = self._coercion(parameter['value'], parameter['parameterType'])
                    paramValue = paramValues.get(str(parameter["id"]))
                    if paramValue:
                        value = paramValue
                    config[package["name"]][node["name"]]["ros__parameters"][parameter['name']] = value                                                             
        return config   
    
    def save_config(self, config):        
        import os
        try:
            # print("creating path: ", self.CONFIG_FOLDER)
            os.makedirs(self.CONFIG_FOLDER)
        except FileExistsError:
            # directory already exists
            pass
                
        from ament_index_python.packages import get_package_share_directory
        for package_name, citros_config in config.items():     
            self.log.debug(f"Saving config for [{package_name}]")                               
            # TODO: add other method to get the package path
            path_to_package = None
            try:
                path_to_package = get_package_share_directory(package_name) # get the path to the package install directory - the project must be sourced for it to work            
            except Exception as e:
                self.log.exception(e)
                continue                

            if not path_to_package:
                continue
                
            path = f"{path_to_package}/config/"    
            
            # check if folder exists
            if not Path(path).exists():
                self.log.debug(f"No config file {path} exits for pack:{package_name}. passing.") 
                continue
                                                
            # path = f"install/{package_name}/share/{package_name}/config/"
            Path(path).mkdir(parents=True, exist_ok=True)
            path = path + "params.yaml"
            
            # check if file exists?
            if not Path(path).exists():
                self.log.debug(f"No config file {path} exits for pack:{package_name}. passing.") 
                continue
            
            # self.log.debug(f"Loading default config from {path}") 
            with open(path, "r") as stream:
                try:    
                    default_config = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
            
            # self.log.debug(f"Merging configuration files.") 
            merged_config = {key: value for (key, value) in (list(default_config.items()) + list(citros_config.items()))}
            
            # self.log.debug(f"config file for {package_name}:")
            self.log.debug(json.dumps(merged_config, indent=4))
            
            with open(path, 'w') as file:
                yaml.dump(merged_config, file)  
                
            # save for metadata
            with open(f"{self.CONFIG_FOLDER}/{package_name}.yaml", 'w') as file:                                     
                yaml.dump(merged_config, file)         
    
    def init_params(self, batch_run_id, sid):                
        self.log.info("Getting parameters from CITROS.") 
        config = self.get_config(batch_run_id, sid)
        if not config:
            # if there is no config, cant init anything...
            self.log.warning("If there is no config, cant init anything...") 
            return
        self.log.debug("Saving parameters to files. ")        
        self.save_config(config)     
        self.log.debug("Done saving config files.")                    
        return config
        
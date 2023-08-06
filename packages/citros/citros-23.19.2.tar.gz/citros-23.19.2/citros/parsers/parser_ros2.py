from pygments import highlight, lexers, formatters
from bson import ObjectId
import glob
import json
import yaml
from .parser_base import parser_base
import itertools 

class parser_ros2(parser_base):
    def __init__(self, logging) -> None:                                
        self.log = logging
        
        self.project = None

    def print(self, json_data):
        formatted_json = json.dumps(json_data, indent=4, default=str)
        self.log.info(formatted_json)
        # colorful_json = highlight(bytes(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
        # self.log.debug(colorful_json)

    # Any lang
    def parse_xml(self, package_path):    
        import xml.etree.ElementTree as ET
        path_to_package_xml = f"{package_path}/package.xml"                
        tree = ET.parse(path_to_package_xml)
        root = tree.getroot()
        
        return {
            "package_xml": path_to_package_xml,
            
            "package_name": root.find("name").text,
            "version": root.find("version").text,
            "maintainer": root.find("maintainer").text,
            "maintainer_email": root.find("maintainer").attrib["email"],
            "description": root.find("description").text,
            "license": root.find("license").text,
            "nodes": [],
            "build_type": root.find("export").find("build_type").text,
        }
    
    # C / CPP
    def parse_makefile(self, package_path):        
        import re
        path_to_cmake = f"{package_path}/CMakeLists.txt"        
        f = open(path_to_cmake, "r")
        package_py_content = f.read()          
        # nodes_list = re.search("(?<=install\(TARGETS)($[\S\s]*)(?=DESTINATION)", package_py_content)
        matches = re.finditer(r"install\(TARGETS([\S\s]*?)DESTINATION", package_py_content, re.MULTILINE)
        
        #(?<=install\(TARGETS)($[\S\s]*)(?=^\))
        nodes = []
        for matchNum, match in enumerate(matches, start=1):
            matches = match.groups()[0].split("\n")            
            for n in matches:   
                node = n.strip()                     
                if node == "":
                    continue             
                if node[0] == "#":
                    continue                
                nodes.append({                                    
                    "name": node,
                    "entry_point": "",                    
                    "path": "",
                    "parameters": []
                })        
        return {
            "cmake": path_to_cmake,
            "nodes": nodes 
        }               
    
    # Python
    def parse_setup_py(self, package_path):
        import ast
        
        path_to_setup = f"{package_path}/setup.py"        
        f = open(path_to_setup, "r")
        package_py_contgent = f.read()            
        tree = ast.parse(package_py_contgent)       
        # print("0000000000000000000000000000000000000000000000000000000000000000")
        # print(ast.dump(tree, indent=4))
    
        # package_name = package_path.split('/')[-1]
        # for el in tree.body:
        #     if(type(el) == ast.Assign and el.targets[0].id == 'package_name'):
        #         print("value:", el.targets[0].id)
        #         print("value:", el.value.value)
            
        # package_name = tree.body[3].value.value
        package_name = package_path.split("/")[-1]
        
        version = tree.body[-1].value.keywords[1].value.value
        maintainer = tree.body[-1].value.keywords[6].value.value
        maintainer_email = tree.body[-1].value.keywords[7].value.value
        description = tree.body[-1].value.keywords[8].value.value
        license = tree.body[-1].value.keywords[9].value.value
            
        nodes = []
        for x in tree.body[-1].value.keywords[11].value.values[0].elts:
            node_name = x.value.split("=")[0].replace(" ", "")
            nodes.append({                
                "name": node_name,
                "entry_point": x.value.split("=")[1].replace(" ", ""),                

                "path": f"{package_path}/{package_name}/{x.value.split('=')[1].replace(' ', '').split(':')[0].split('.')[1]}.py",
                "parameters": []
            })
                
        return {
            "setup_py": path_to_setup,
            
            "package_name": package_name,
            "version": version,
            "maintainer": maintainer,
            "maintainer_email": maintainer_email,
            "description": description,
            "license": license,
            "nodes": nodes
        }
    
    def get_project_packages(self, project_path, workspace=""):                
        self.log.debug(f" + get_project_packages {project_path}/{workspace}")
        
        package_paths = glob.glob(f"{project_path}/src/*")                
        if workspace != "":
            package_paths = glob.glob(f"{project_path}/{workspace}/src/*") + package_paths            
        
        package_paths = [p for p in package_paths if 'ros2.' not in p]
        
        packages = []
        for package_path in package_paths:            
            # package_py = f"{'/'.join(package_path.split('/')[:-1])}/setup.py"
            self.log.debug(f"package_path: {package_path}")
            
            parsed_data = None     
            try:
                parsed_data = self.parse_xml(package_path)
            except Exception as e:
                print(f"{package_path} doesn't contain xml, probably not a package. skipping.")
                continue
            
            if parsed_data["build_type"] == "ament_python":                
                temp = self.parse_setup_py(package_path)
                parsed_data["nodes"] = temp["nodes"]                
                parsed_data["setup_py"] = temp["setup_py"]
                
            elif parsed_data["build_type"] == "ament_cmake":          
                temp = self.parse_makefile(package_path)
                parsed_data["nodes"] = temp["nodes"]
                parsed_data["cmake"] = temp["cmake"]                
                
            else:
                self.log.exception(f"Method {parsed_data['build_type']} not allowed")
                raise Exception(f"Method {parsed_data['build_type']} not allowed")

            node_parameters = {}
            try:
                path_to_config =  f"{package_path}/config/params.yaml"            
                with open(path_to_config, 'r') as config_file:
                    config = yaml.full_load(config_file)                    
                    
                for node_name, val in config.items():
                    par_dict = val["ros__parameters"]                    
                    node_parameters[node_name] = []
                    for key, val in par_dict.items():
                        node_parameters[node_name].append({                            
                            "name":key,
                            "parameterType": type(val).__name__, # TODO: Fix type
                            "value": val,
                            "description": "Parameter loaded from config.yaml",                            
                        })
                for node in parsed_data["nodes"]:
                    # print(f"adding parameters to [{node['name']}] node")                
                    node["parameters"] = node_parameters.get(node["name"], [])                    
            except Exception as e:
                self.log.exception(e)

            packages.append({
                # "id": uuid.uuid4(),                
                "name": parsed_data["package_name"],
                "cover": "",
                "path": package_path,
                "setup_py": parsed_data.get("setup_py", ""),
                "package_xml": parsed_data.get("package_xml"),
                "maintainer": parsed_data.get("maintainer"),
                "maintainer_email" : parsed_data.get("maintainer_email"),
                "description": parsed_data.get("description"),
                "license": parsed_data.get("license"),

                "readme": f"{package_path}/README.md",
                "git": "", #TODO
                
                "launches": self.get_project_launch_files(package_path),
                "nodes": parsed_data.get("nodes"),                
            })
        return packages

    def get_project_launch_files(self, package_path, workspace=""):
        #TODO: check if done. 
        launch_paths = glob.glob(f"{package_path}/launch/*.py")
        if workspace != "":
            launch_paths + glob.glob(f"{package_path}/{workspace}/src/*.py")
        
        launch_paths = [p for p in launch_paths if 'ros2.' not in p]
        
        launche_files = []
        for launch_path in launch_paths:
            launche_files.append({                
                "name": launch_path.split("/")[-1],
                "path": launch_path,

                # "tags": [],
                "description": "",                
            })
        return launche_files
    
    def get_project_git(self, project_path):
        #TODO
        return ""

    def get_project_description(self, project_path):
        #TODO
        return ""

    def get_file_content(self, path):
        try:
            content = ''
            f = open(path, "r")
            content = f.read() 
            f.close()           
            return content
        except Exception:
            return ""        
    
    def parse(self, project_path, project_name, workspaces=["", "ros_ws"]):       
        packages = []
        launches = []
        for w in workspaces:
            packages = packages + self.get_project_packages(project_path, workspace=w)
            launches = launches + self.get_project_launch_files(project_path, workspace=w)
                        
        if not self.project:
            self.project = {                          
                "cover": "",
                "name": project_name,
                "image": project_name,
                "tags": [],
                "is_active": True,
                "description": self.get_project_description(project_path),                     
                "git": self.get_project_git(project_path), 
                "path": project_path,    
                                
                "packages": packages,                
                "launches": launches,

                "readme": self.get_file_content(f"{project_path}/README.md"),
                "license": self.get_file_content(f"{project_path}/LICENSE"),
            }
        else:
            self.project[0]["cover"] = ""
            self.project[0]["name"] = project_path.split("/")[-1]
            self.project[0]["image"] = self.project[0]["name"]

            self.project[0]["description"] = self.get_project_description(project_path)
            self.project[0]["git"] = self.get_project_git(project_path)
            
            self.project[0]["packages"] = list(itertools.chain([self.get_project_packages(project_path, workspace=w) for w in workspaces])) ,
            self.project[0]["launches"] = list(itertools.chain([self.get_project_launch_files(project_path, workspace=w) for w in workspaces])),
        
        return self.project



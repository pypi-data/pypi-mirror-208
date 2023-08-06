from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
import json

class citros_integration():
    """citros_integration class has all the functionality to integrate the project to CiTROS"""
    def __init__(self, citros) -> None:
        # Select your transport with a defined url endpoint        
        self.citros = citros
        self.log = citros.log

    def uploadParam(self, param, node_id):    
        """

        :param param: 
        :param node_id: 
        """
        # print("uploadParam for node_id: ", node_id)      
        query = """
        mutation UpsertRosNodeParameter($node_id: UUID!, $name: String!, $description: String!, $value: String!, $parameterType: ParameterType) {
            upsertRosNodeParameter(
                where: {rosNodeId: $node_id, name: $name }
                input: {rosNodeParameter: {rosNodeId: $node_id, name: $name, description: $description, parameterType: $parameterType, value: $value}}                
            ) {
                rosNodeParameter {                    
                    id
                }               
            }
        }
        """
        
        print(f" - - - Parameter: {param['name']}")
        param["node_id"] = node_id
        param["value"] = str(param["value"])
        param["parameterType"] = param["parameterType"].upper()        
        if param["parameterType"] == 'LIST':
            print('*********************************************************')
            print(f'*** ERROR: parameterType {param["parameterType"]} not supported. passing. ****')
            print('*********************************************************')
            return
        
        result = self.citros.gql_execute(query, variable_values=param)
        # print(result)
        param_id = result["upsertRosNodeParameter"]["rosNodeParameter"]["id"]
        print(" - - - param_id", param_id)
        return param_id 
    
    def uploadNode(self, node, package_id):      
        """

        :param node: 
        :param package_id: 

        """
        # print("uploadNode for package_id: ", package_id)  
        query = """
        mutation UpsertRosNode($package_id: UUID!, $name: String!, $path: String!) {
            upsertRosNode(
                where: {
                    name: $name,
                }
                input: {rosNode: {packageId: $package_id, name: $name, path: $path}}
            ) {
                rosNode {
                id
                }
            }
        }
        """
        
        node["package_id"] = package_id
        result = self.citros.gql_execute(query, variable_values=node)
        
        node_id = result["upsertRosNode"]["rosNode"]["id"]
        print(f" - - node: {node['name']} [{node_id}]")
        
        print(" - - - parameters: ")
        for parameter in node["parameters"]:
            parameter_id = self.uploadParam(parameter, node_id)            
    
        return node_id  
    
    def uploadLaunch(self, launch, package_id):        
        """

        :param launch: 
        :param package_id: 

        """
        # print("uploadLaunch for package_id: ", package_id)        
        query = """
        mutation upsertLaunch($data: UpsertLaunchInput!){
            upsertLaunch(input:$data) {
                launch{
                id
                name
                }
            }
        }
        """
        
        print("Launch: ")
        launch["packageId"] = package_id                
        result = self.citros.gql_execute(query, variable_values={
            "data":{
                "launch":launch
            }
        })
        # print("result", result)
        launch_id = result["upsertLaunch"]["launch"]["id"]
        print(" - launch_id", launch_id)
        return launch_id  
        
    def uploadPackage(self, package, project_id):
        """

        :param package: 
        :param project_id: 

        """
        # print("uploadPackage for project_id: ", project_id)
        query = """
        mutation UpsertRosPackage(
            $projectId: UUID!, 
            $name: String!,
            $cover: String!,
            $description: String!,
            $git: String!,
            $license: String!,
            $maintainer: String!,
            $maintainer_email: Email!,
            $path: String!,
            $readme: String!,
            $setup_py: String!,
        ) {
        upsertRosPackage(
            where: {
                name: $name,
            }
            input: {rosPackage: {
                projectId: $projectId, 
                name: $name, 
                cover: $cover, 
                description: $description, 
                git: $git,                 
                license: $license, 
                maintainer: $maintainer, 
                maintainerEmail: $maintainer_email, 
                path: $path, 
                readme: $readme, 
                setupPy: $setup_py
            }}) {
                rosPackage {
                    id
                }
            }
        }
        """
        
        package["projectId"] = project_id
        result = self.citros.gql_execute(query, variable_values=package)
        # print(result)
        package_id = result["upsertRosPackage"]["rosPackage"]["id"]        
        print(f" - package: {package['name']} [{package_id}]")
                
        for node in package["nodes"]:
            node_id = self.uploadNode(node, package_id)            
                                
        for launch in package["launches"]:
            launch_id = self.uploadLaunch(launch, package_id)             
            
        return package_id        
    
    def sync_project(self, project):
        """

        :param project: 

        """
        if not self.citros.isAuthenticated():                                
            self.log.error("Cant sync unauthenticated user. please log in first.")
            return
            
        query = """
            mutation UpsertProject(
                $name: String!, 
                $image: String!,
                $is_active: Boolean!,
                $cover: String!,
                $description: String!,
                $git: String!,
                $license: String!,
                $path: String!, 
                $readme: String!,
                $userId: UUID!
                ) {
            upsertProject(
                where: {
                    name: $name, 
                    userId: $userId
                }
                input: {
                    project: {
                        isActive: $is_active, 
                        name: $name, 
                        image: $image,
                        cover: $cover, 
                        description: $description, 
                        git: $git, 
                        license: $license, 
                        path: $path, 
                        readme: $readme, 
                        userId: $userId
                    }
                }) {
                    project {                                            
                        id
                    }                    
                }
            }
            """
        # print("Project: ")
        print("-------------------sync_project-------------------")     
        project["userId"] = self.citros.getUser().get("id")
        # print("user_id", self.citros.user.get("id"))
        # print("user", self.citros.user)
        result = self.citros.gql_execute(query, variable_values=project)
        # print("result:", result)
        project_id = result["upsertProject"]["project"]["id"]   
        print(f"project_id: {project['name']} [{project_id}]")         
                
        # print("Packages: ")
        for package in project["packages"]:
            package_id = self.uploadPackage(package, project_id)
        print("----------------------DONE------------------------")               
        
        return project_id        
        
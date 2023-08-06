import os 
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer
import shutil

def isDeployed():
    flag_value = os.getenv("ECIDA_DEPLOY", "").lower()
    return flag_value == "true"

def now():
    return "[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]"


def convert_to_dns_name(string):
    # Convert the string to lowercase
    string = string.lower()
    
    # Replace non-alphanumeric characters with hyphens
    string = ''.join('-' if not c.isalnum() else c for c in string)
    
    # Remove leading and trailing hyphens
    string = string.strip('-')
    
    # Replace multiple consecutive hyphens with a single hyphen
    string = '-'.join(filter(None, string.split('-')))
    
    # Ensure the resulting string is not empty
    if not string:
        raise ValueError("Invalid string: Cannot convert to DNS name.")
    
    return string

def create_directory(directory_path):
    if os.path.exists(directory_path):
        print(f"Deleting existing directory: {directory_path}")
        shutil.rmtree(directory_path)

    try:
        print(f"Creating directory: {directory_path}")
        os.mkdir(directory_path)
    except OSError as e:
        print(f"Failed to create directory: {directory_path}")
        print(f"Error: {str(e)}")    

class EcidaModule:
    def __init__(self, name, version):
        self._name = name
        self._version = version
        self._inputs = {}
        self._outputs = {}
        self._topics_envVars = {}
        self._topics_names = {}
        self._consumers = {}
        self._directories = {}        
        self._producer = None
        self._initialized = False
        self._deployed = isDeployed()
    
    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version
    
    @property
    def topics_envVars(self):
        return self._topics_envVars

    @property
    def inputs(self):
        return self._inputs
    
    @property
    def outputs(self):
        return self._outputs
    
    @property
    def directories(self):
        return self._directories
    
    @name.setter
    def name(self, value):
        raise AttributeError("Attribute is read-only")

    @version.setter
    def version(self, value):
        raise AttributeError("Attribute is read-only")
    
    @version.setter
    def deployed(self, value):
        raise AttributeError("Attribute is read-only")
    
    def add_input(self, inp: str, type):
        self._inputs[inp] = type
        self._topics_envVars[inp] = "KAFKA_TOPIC_"+ inp.upper()
        
    def add_output(self, out: str, type):
        self._outputs[out] = type
        self._topics_envVars[out] = "KAFKA_TOPIC_"+ out.upper()
        
    def add_input_directory(self, inp: str):
        localPath = convert_to_dns_name(inp)
        self._inputs[inp] = "directory"
        self.directories[inp] = {}
        self.directories[inp]["localPath"] = localPath
        
    def add_output_directory(self, out: str):
        localPath = convert_to_dns_name(out)
        self._outputs[out] = "directory"
        self.directories[out] = {}
        self.directories[out]["localPath"] = localPath
        
    def add_input_from_git(self, name: str, git: str, path: str):
        self.add_input_directory(name)
        self.__add_git_to_directory(name, git,path)
    
    def add_output_to_git(self, name: str, git: str, path: str):
        self.add_output_directory(name)
        self.__add_git_to_directory(name, git,path)
        
    def get_path(self, name):
        if self._deployed:
            return "/"+self.directories[name]["localPath"]
        else:
            return "./"+self.directories[name]["localPath"]
    
    def __add_git_to_directory(self, name: str, git: str, path: str):
        self._directories[name]["source"] = git
        self._directories[name]["folder"] = path
    
    def to_yaml(self) -> str:
        return str(self._inputs) + "\n" + str(self._outputs)
    
    def initialize(self):
        if self._deployed == True:
            isKafka = False
            for _, value in self._inputs.items():
                if value != "directory":
                    isKafka = True
                    
            if isKafka:
                self._KAFKA_BOOTSTRAP_SERVER = os.environ['KAFKA_BOOTSTRAP_SERVER']
                self._KAFKA_SASL_MECHANISM = os.environ['KAFKA_SASL_MECHANISM']
                self._KAFKA_SECURITY_PROTOCOL = os.environ['KAFKA_SECURITY_PROTOCOL']
                self._KAFKA_USERNAME = os.environ['KAFKA_USERNAME']
                self._KAFKA_PASSWORD = os.environ['KAFKA_PASSWORD']
                self._KAFKA_GROUP_ID = os.environ['KAFKA_USERNAME']
            
            for key, value in self._inputs.items():
                if value == "directory":
                    continue
                topicName = os.environ[self._topics_envVars[key]]
                self._topics_names[key] = topicName
                consumer = KafkaConsumer(topicName, bootstrap_servers = self._KAFKA_BOOTSTRAP_SERVER, 
                                sasl_plain_username= self._KAFKA_USERNAME,
                                sasl_plain_password= self._KAFKA_PASSWORD,
                                sasl_mechanism=self._KAFKA_SASL_MECHANISM,
                                security_protocol=self._KAFKA_SECURITY_PROTOCOL,
                                group_id= self._KAFKA_GROUP_ID)
                self._consumers[key] = consumer
                
            if len(self._outputs) > 0 and isKafka:
                self._producer = KafkaProducer(bootstrap_servers = self._KAFKA_BOOTSTRAP_SERVER,
                                sasl_plain_username= self._KAFKA_USERNAME,
                                sasl_plain_password= self._KAFKA_PASSWORD,
                                sasl_mechanism=self._KAFKA_SASL_MECHANISM,
                                security_protocol=self._KAFKA_SECURITY_PROTOCOL)
            
            for key, value in self._outputs.items() :
                if value == "directory":
                    continue
                topicName = os.environ[self._topics_envVars[key]]
                self._topics_names[key] = topicName
            
            self._initialized = True

        else:
            for output in self._outputs:
                if output in self._directories:
                    path = self.get_path(self._directories[output]["localPath"])
                    create_directory(path)

            
  
    def push(self, output_channel: str, message) -> bool:
        if self._deployed:
            if output_channel in self._outputs:
                self._producer.send(self._topics_names[output_channel], value= str(message).encode("utf-8"))
                return True
            return False
        else:
            return print(f"{now()} {output_channel}: {message}")
    
    def pull(self, input_channel: str) -> any:
        if self._deployed:
            if input_channel in self._inputs:
                for msg in self._consumers[input_channel]:
                    return msg.value.decode("utf-8")
            return None
        else:
            return input(f"{now()} {input_channel}:")
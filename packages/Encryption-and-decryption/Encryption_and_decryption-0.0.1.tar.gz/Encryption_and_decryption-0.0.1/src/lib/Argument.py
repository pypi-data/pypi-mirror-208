class Argument:
    def __init__(self,argument):
        self.argument=argument
        self.command=[]
        self.option=[]
        self.option_values={}
        for arg in self.argument:
            if '-' in arg:
                if ':' in arg:
                    keyValue=arg.split(':')
                    self.option.append(keyValue[0])
                    self.option_values[keyValue[0]]=keyValue[1]  
                else:
                    self.option.append(arg)
            else:
                self.command.append(arg)
                
                
    def hasCommands(self,commands:list):
        user_command=set(self.command)
        required_command=set(commands)
        return list(required_command & user_command)
    
    def hasOption(self,options:list): 
        user_options=set(self.option)
        required_option=set(options)
        return list(required_option & user_options)
    
    def getoptionvalue(self, option, default=None):
        if option in self.option_values:
            return self.option_values[option]
        else:
            return default
        
    def hasOptionValue(self, option):
        check_option = option in self.option_values
        return check_option
    

        

import argparse

class PyntSubCommand:
    def __init__(self, name) -> None:
        self.name = name
        pass 

    def get_name(self):
        return self.name
    
    def add_cmd(self, parent: argparse._SubParsersAction) -> argparse.ArgumentParser: 
        raise NotImplemented()
    
    def run_cmd(self, args: argparse.Namespace): 
        raise NotImplemented()

import subprocess
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

class ProtocBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        """
        This method is called before the build process starts.
        """
        print("--- Running Protoc Build Hook via doit ---")

        result = subprocess.run(
            ["doit", "build_protos"], 
            check=True,
        )


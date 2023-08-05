from .core import make
import fire
version = "1.0.1"

class CLI :
    def __init__(self):
        self.make = make
    def version(self):
        print(f"Ar Site Maker {version}")

    def __str__(self):
        return f"Ar Site Maker {version}\n Documentation is here https://github.com/enfy-space/ArSiteMaker"



def cli():
    fire.Fire(CLI())

if __name__ == "__main__":
    fire.Fire(make)

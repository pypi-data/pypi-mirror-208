from enum import Enum

class Engine(Enum):
    OPENAI = "openai"

if __name__ == '__main__':
    print(Engine.__members__)



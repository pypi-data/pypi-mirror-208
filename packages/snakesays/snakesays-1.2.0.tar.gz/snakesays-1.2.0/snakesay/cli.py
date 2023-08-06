import sys
from snakesay import snake

def snakesay():
    snake.say(" ".join(sys.argv[1:]))

if __name__ =="__main__":
    snakesay()
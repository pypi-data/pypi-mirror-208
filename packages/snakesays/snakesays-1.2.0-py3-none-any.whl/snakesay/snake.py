snake = r"""             /
            /
       __  /
      {00}
      (__)\
       ?? \\
          _\\__
         (_____)_
         (______)Oo*
"""

def bubble(message):
    bubble_length = len(message) + 2
    return f"""
    {"_"*bubble_length}
    ({message})
    {"-"*bubble_length}"""

def say(message):
    print(bubble(message))
    print(snake)

from librenv.librenv import LibreNV 
import sys

def main():
    if len(sys.argv) < 2: 
        print("Error: Project path not setted!")
        exit(1)
    librenv = LibreNV()
    exit(librenv.load_game(sys.argv[1]))

if __name__ == "__main__":
    main()

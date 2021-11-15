import numpy as np
import time

def combine_dict(d1, d2):
    return {key: d1[key] + d2[key] for key in d1}
    
def main():
    d1 = {'1': 1, '2': 2}
    d2 = {'1': 3, '2': 4}
    print(combine_dict(d1,d2))

if __name__ == "__main__":
    main()
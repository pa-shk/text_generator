import random
import dill
import re
import argparse
import sys


if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', type=str, required=True, help='path to save model')
    parser.add_argument('-p', '--prefix', type=str, help='words to start generating text')
    parser.add_argument('-l', '--length', type=int, required=True, help='length of generated sequence')
    args = parser.parse_args()
    # model was developed under python 3.8
    if sys.version_info[0:2] != (3, 8):
        raise Exception('Requires python 3.8')
    # load model
    with open(args.model , 'rb') as f:
        model = dill.load(f)
    # generate text
    print(model.generate(args.length, start=args.prefix))

#!/usr/bin/env python

import argparse
import torch


parser = argparse.ArgumentParser()
parser.add_argument('model', type=str)
parser.add_argument('device', type=str, choices=['cuda', 'cpu'])
args = parser.parse_args()

if not torch.cuda.is_available() and args.device == 'cuda':
    raise EnvironmentError('Need to run this on a machine with GPU! Converted model in this state is broken, revert to CPU or rerun on other machine.')

device = torch.device(args.device)

model = torch.jit.load(args.model, map_location=device)
model.save(args.model)
#!/usr/bin/env blender
import sys
import os

import bpy
import addon_utils

envPaths = [
  os.getcwd(),
  os.getcwd() + "/io_BlenderEdmExporter" 
]

for envPath in envPaths:
  print( " Added to path:", envPath )
  sys.path.append( envPath )

import io_BlenderEdmExporter

def _main(args):
  io_BlenderEdmExporter.register()

if __name__ == "__main__":
  if _main(sys.argv) == -1:
    sys.exit() 
    
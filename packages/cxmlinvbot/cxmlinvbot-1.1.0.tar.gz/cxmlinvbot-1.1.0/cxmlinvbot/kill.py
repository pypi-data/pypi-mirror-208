import glob
import os

from   local.config.env import EnvConfig


def main():
  graceFiles = glob.glob('*.grace', root_dir=EnvConfig.PROJECT_FULLPATH)
  for gf in graceFiles:
    os.remove(gf)
   

if __name__ == "__main__":
  main()
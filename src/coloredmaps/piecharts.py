import click
import pathlib
import json
import os
from coloredmaps.ratio import COLORED, MONOCHROME
import matplotlib.pyplot as plt

@click.command()
@click.option('-i', '--input-dir', help='Input directory')
@click.option('-r', '--ratio', help='Ratio parameter', default=0.25)
def main(input_dir, ratio):
  for map_ in COLORED + MONOCHROME:
      stem = pathlib.Path(map_).stem
      with open(os.path.join(input_dir, f"{stem}", f"{stem}.json"), 'r') as fd:
          results = json.load(fd)
      plt.pie([results[p]['size'] for p in results], colors=[[x / 255.0 for x in results[p]['center']] for p in results], labels=[str(results[p]['center']) for p in results])
      plt.savefig(pathlib.Path(input_dir) / f"{stem}_colors.svg")
      plt.figure(figsize=(10,10))

if __name__ == '__main__':
  main()

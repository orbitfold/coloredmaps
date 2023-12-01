import click
import pathlib
import json

COLORED = [
  '28_6404_4_fbg.jpg', '28_6506_4_fbg.jpg', '28_6605_D.jpg', 
  '28_6607_D.jpg', '28_6608_D.jpg', '28_6609_D.jpg', 
  '29_6508_4_fbg.jpg', '29_6610_D.jpg', '29_6705_SuGmbl.jpg', 
  '29_6707_D.jpg', 'BayHStA_OBB_12856_0001.tif', 'BayHStA_OBB_KuPl_6811_0013.tif',
  'M-32-10-A-a-Vienenburg-1984.bmp', 'M-32-10-A-b-Osterwieck-1985.bmp', 'M-32-10-A-c-Bad_Harzburg-1984.bmp',
  'M-32-10-A-d-Ilsenburg_(Harz)-1985.bmp', 'M-32-10-A-c-Bad_Harzburg-1984.bmp', 'M-32-10-A-d-Ilsenburg_(Harz)-1985.bmp',
  'M-32-10-B-a-Dardesheim-1985.bmp', 'M-32-10-B-b-Badersleben-1985.bmp', 'M-32-10-B-c-Wernigerode-1985.bmp',
  'M-32-10-B-d-Derenburg-1985.bmp', 'M-32-10-C-a-Brocken-1984.bmp', 'M-32-10-C-b-Schierke-1985.bmp',
  'MA_Karten_und_Plaene_308_0001.tif', 'MA_Karten_und_Plaene_308_0003.tif', 'N-32-72-D-a-Ostseebad_Kuehlungsborn-1989.bmp', 
  'N-32-72-D-b-Bad_Doberan-1989.bmp', 'N-32-82-A-b-Bad_Schwartau-1984.bmp', 'N-32-82-D-c-Ratzeburg-1990.bmp', 
  'N-32-83-B-d-Wismar-1990.bmp', 'N-32-94-D-b-Bennin-1989.bmp', 'N-32-95-A-d-Duemmer-1990.bmp',
  'N-32-95-B-b-Schwerin-1990.bmp', 'PLS_9771_01.tif'
]

MONOCHROME = [
  'df_dk_0010001_1725.tif', 'df_dk_0010001_2343.tif', 'df_dk_0010001_4643_1938.tif',
  'df_dk_0010001_4902_1934.tif', 'df_dk_0010001_6714.tif', 'Landesvermessungsamt-Flurkartenarchiv_0002.tif',
  'Landesvermessungsamt-Flurkartenarchiv_0003.tif', 'MA_Karten_und_Plaene_315_0001.tif', 'MA_Karten_und_Plaene_315_0002.tif',
  'MA_Karten_und_Plaene_315_0003.tif', 'MA_Karten_und_Plaene_315_0004.tif', 'MA_Karten_und_Plaene_318_0023.tif',
  'MA_Karten_und_Plaene_318_0024.tif', 'MA_Karten_und_Plaene_318_0025.tif', 'MA_Karten_und_Plaene_318_0026.tif',
  'MA_Karten_und_Plaene_318_0027.tif', 'MA_Karten_und_Plaene_318_0028.tif', 'MA_Karten_und_Plaene_318_0029.tif',
  'MA_Karten_und_Plaene_393_0001.tif', 'MA_Karten_und_Plaene_393_0002.tif', 'MA_Karten_und_Plaene_393_0003.tif',
  'MA_Karten_und_Plaene_394_0001.tif', 'MA_Karten_und_Plaene_394_0002.tif', 'MF_KuPL_332_2_0001.tif',
  'MF_KuPL_380_0001.tif', 'Pls_8540_0008.tif', 'Pls_8540_0014.tif' 
]

@click.command()
@click.option('-i', '--input-dir', help='Input directory')
@click.option('-r', '--ratio', help='Ratio parameter', default=0.25)
def main(input_dir, ratio):
  confusion = {
    'colored': {'colored': 0, 'monochrome': 0},
    'monochrome': {'colored': 0, 'monochrome': 0}
  }
  for c_map in COLORED:
    with open(os.path.join(input_dir, c_map), 'r') as fd:
      data = json.load(fd)
      sizes = [data[key]['size'] for key in data]
      sizes = sorted(sizes)
      r = sizes[-1] / float(sum(sizes[:-1]))
      if r < ratio:
        confusion['colored']['monochrome'] += 1
      else:
        confusion['colored']['colored'] += 1
  for m_map in MONOCHROME:
    with open(os.path.join(input_dir, c_map), 'r') as fd:
      data = json.load(fd)
      sizes = [data[key]['size'] for key in data]
      sizes = sorted(sizes)
      r = sizes[-1] / float(sum(sizes[:-1]))
      if r < ratio:
        confusion['monochrome']['monochrome'] += 1
      else:
        confusion['monochrome']['colored'] += 1
  print(confusion)

if __name__ == '__main__':
  main()

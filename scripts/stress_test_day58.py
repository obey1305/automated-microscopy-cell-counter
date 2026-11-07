"""Reproducible synthetic stress cases; these are not biological validation."""
from pathlib import Path
import os
ROOT=Path(__file__).resolve().parents[1]
os.environ['CELLPOSE_LOCAL_MODELS_PATH']=str(ROOT/'.cellpose/models')
import sys
sys.path.insert(0,str(ROOT))
import json
import numpy as np
import tifffile
import torch
from PIL import Image
from cellpose import models
from scripts.image_tools import load_image, numbered_overlay
from scripts.reporting import evaluate_predictions


def make_case(kind):
    rng=np.random.default_rng(58)
    y,x=np.mgrid[:256,:256]
    gt=np.zeros((256,256),dtype=np.uint16)
    image=np.full((256,256),30.0)
    centers=[(r,c) for r in range(35,235,37) for c in range(35,235,37)]
    if kind=='overlapping':
        centers=[(r,c+d) for r in (50,125,200) for c in (50,135,210) for d in (-10,10)]
    radius=20 if kind in ('crowded','overlapping') else 14
    amplitude=8 if kind=='low_contrast' else 130
    for i,(cy,cx) in enumerate(centers,1):
        distance=((y-cy)/radius)**2+((x-cx)/(radius*0.85))**2
        region=distance<=1
        gt[region]=i
        image[region]=np.maximum(image[region],30+amplitude*(0.7+0.3*(1-distance[region])))
    image+=rng.normal(0,3,image.shape)
    return np.clip(image,0,255).astype(np.uint8),gt


def main():
    output=ROOT/'results/day58'
    output.mkdir(parents=True,exist_ok=True)
    device=torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
    model=models.CellposeModel(pretrained_model='cpsam_v2',device=device,use_bfloat16=False)
    rows=[]
    for kind in ('crowded','overlapping','low_contrast'):
        image,gt=make_case(kind)
        path=output/f'{kind}.png'
        Image.fromarray(image).save(path)
        image=load_image(path.read_bytes(),path.name)
        masks,_,_=model.eval(image,batch_size=1,normalize=True,min_size=15)
        overlay,positions=numbered_overlay(image,masks)
        Image.fromarray(overlay).save(output/f'{kind}_overlay.png')
        tifffile.imwrite(output/f'{kind}_masks.tif',masks.astype(np.uint32))
        row=dict(case=kind,synthetic=True,**evaluate_predictions(masks,gt,len(np.unique(gt[gt>0]))))
        rows.append(row)
        print(json.dumps(row),flush=True)
    (output/'stress_results.json').write_text(json.dumps(rows,indent=2)+'\n')


if __name__=='__main__': main()

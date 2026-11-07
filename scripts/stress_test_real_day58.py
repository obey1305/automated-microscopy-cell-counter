"""Local real-image crop and contrast perturbation checks, not independent validation."""
from pathlib import Path
import os,sys,json
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root));os.environ['CELLPOSE_LOCAL_MODELS_PATH']=str(root/'.cellpose/models')
import numpy as np,tifffile,torch
from PIL import Image
from cellpose import models
from scripts.reporting import evaluate_predictions
from scripts.cell_analysis import count_cells
from scripts.image_tools import numbered_overlay
p=root/'data/raw/Fluo-N2DH-GOWT1/Fluo-N2DH-GOWT1'
a=tifffile.imread(p/'02/t001.tif');g=tifffile.imread(p/'02_GT/SEG/man_seg001.tif');t=tifffile.imread(p/'02_GT/TRA/man_track001.tif')
# Fixed dense central crop and touching-nucleus crop; derived from the real frame.
cases=[('real_cluster_crop',a[180:700,180:700],g[180:700,180:700],t[180:700,180:700]),('real_touching_crop',a[60:400,120:500],g[60:400,120:500],t[60:400,120:500])]
rng=np.random.default_rng(59)
low=np.clip(100+a.astype(float)*0.12+rng.normal(0,1.5,a.shape),0,255).astype(np.uint8)
cases.append(('real_low_contrast_derived',low,g,t))
m=models.CellposeModel(pretrained_model='cpsam_v2',device=torch.device('mps'),use_bfloat16=False)
rows=[]
for name,image,gt,track in cases:
 pred,_,_=m.eval(image,batch_size=1,normalize=True,min_size=15)
 overlay,_=numbered_overlay(image,pred)
 Image.fromarray(image).save(root/f'results/day58/{name}.png')
 Image.fromarray(overlay).save(root/f'results/day58/{name}_overlay.png')
 row=dict(case=name,**evaluate_predictions(pred,gt,count_cells(track)))
 rows.append(row);print(json.dumps(row),flush=True)
(root/'results/day58/real_stress_results.json').write_text(json.dumps(rows,indent=2))

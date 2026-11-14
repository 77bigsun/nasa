"""Public numeric Diviner and PGDA products for the fixed Site01 study window."""
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import httpx
import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.warp import transform
from rasterio.windows import Window
from .run import download, save_json

PDS='https://pds-geosciences.wustl.edu/lro/urn-nasa-pds-lro_diviner_derived1/'
LAT=-89.43875806135662
LON=-137.07748292362447


def fetch_range(client,url,path,first,last,total):
    sidecar=path.with_suffix(path.suffix+'.metadata.json')
    import json
    if path.exists() and sidecar.exists():
        metadata=json.loads(sidecar.read_text(encoding='utf-8'))
        if metadata['sha256']==hashlib.sha256(path.read_bytes()).hexdigest():
            return path.read_bytes(),metadata
    response=client.get(url,headers={'Range':f'bytes={first}-{last}'})
    response.raise_for_status()
    if response.status_code!=206 or response.headers.get('content-range')!=f'bytes {first}-{last}/{total}':
        raise ValueError('Unexpected numeric-product byte range')
    if len(response.content)!=last-first+1:raise ValueError('Truncated numeric product')
    path.write_bytes(response.content)
    metadata={'url':url,'byte_range':[first,last],'total_source_bytes':total,
              'sha256':hashlib.sha256(response.content).hexdigest(),
              'hash_kind':'downloaded byte range, not complete source product',
              'retrieved_at':datetime.now(timezone.utc).isoformat()}
    save_json(sidecar,metadata)
    return response.content,metadata


def run(output_dir):
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    with httpx.Client(timeout=180,follow_redirects=True) as client:
        # Public fixed-width GCP geometry is longitude-major, latitude, local time.
        url=PDS+'data_derived_gcp/global_cumul_avg_cyl_90s80s_002.tab'
        col=int(np.floor((LON+180)*2));row=int(np.floor((LAT+90)*2))
        first=(1+(col*20+row)*96)*113
        raw,metadata=fetch_range(client,url,out/'gcp_target_rows.csv',first,first+96*113-1,156211313)
        rows=np.asarray([[float(v) for v in line.split(',')] for line in raw.decode('ascii').splitlines()])
        if rows.shape!=(96,11):raise ValueError('Unexpected Diviner GCP dimensions')
        if not np.allclose(rows[:,0],-180+(col+.5)/2) or not np.allclose(rows[:,1],-90+(row+.5)/2):
            raise ValueError('GCP coordinate mismatch')
        valid=np.isfinite(rows[:,-1])&(rows[:,-1]>0)&(rows[:,-1]!=-9999)
        gcp=dict(metadata,grid_lon=float(rows[0,0]),grid_lat=float(rows[0,1]),requested_lon=LON,
                 requested_lat=LAT,native_grid_degrees=.5,units='K',valid_tbol_count=int(valid.sum()),
                 diurnal_min_K=float(rows[valid,-1].min()),diurnal_max_K=float(rows[valid,-1].max()),
                 rows=rows.tolist())
        save_json(out/'gcp_target.json',gcp)
        # Published containing triangle for this fixed study point; verify it geometrically.
        url=PDS+'data_derived_prp/dlre_prp_south.tab'
        first=(1498754+1)*210
        raw,metadata=fetch_range(client,url,out/'prp_target_row.csv',first,first+209,604800210)
        values=np.asarray([float(v) for v in raw.decode('ascii').strip().split(',')])
        vertices=values[:9].reshape(3,3)
        p,l=np.radians([LAT,LON]);ray=np.array([np.cos(p)*np.cos(l),np.cos(p)*np.sin(l),np.sin(p)])
        u,v,distance=np.linalg.solve(np.column_stack([vertices[1]-vertices[0],vertices[2]-vertices[0],-ray]),-vertices[0])
        if min(u,v,1-u-v)<0 or distance<=0:raise ValueError('Study point outside PRP triangle')
        prp=dict(metadata,range_sha256=metadata['sha256'],centroid_lon=float(values[9]),centroid_lat=float(values[10]),
                 annual_mean_2cm_K=float(values[12]),annual_max_surface_K=float(values[13]),
                 model_stable_ice_depth_m=float(values[14]) if values[14]>=0 else None,
                 requested_lat=LAT,requested_lon=LON,barycentric=[float(1-u-v),float(u),float(v)])
        save_json(out/'prp_target.json',prp)
        for name,url in [
            ('gcp_label.txt',PDS+'data_derived_gcp/global_cumul_avg_cyl_90s80s_002.xml'),
            ('prp_label.txt',PDS+'data_derived_prp/dlre_prp_south.xml')]:
            path=out/name
            if not path.exists():
                response=client.get(url);response.raise_for_status();path.write_bytes(response.content)
        url='https://pgda.gsfc.nasa.gov/data/MoonIllumination/AVGVISIB_85S_060M_201608.TIF'
        path=out/'illumination85s.tif'
        metadata=download(client,url,path)
        with rasterio.open(path) as src:
            xs,ys=transform(CRS.from_proj4('+proj=longlat +R=1737400 +no_defs'),src.crs,[LON],[LAT])
            row,col=src.index(xs[0],ys[0])
            window=src.read(1,window=Window(col-16,row-16,33,33),masked=True).astype(float)
            values=window.filled(np.nan)*src.scales[0]+src.offsets[0]
            illum=dict(metadata,native_pixel_m=60,nodata=src.nodata,scales=list(src.scales),
                point_row=row,point_col=col,lat=LAT,lon=LON,point_fraction=float(values[16,16]),
                window_mean_fraction=float(np.nanmean(values)),quantity='Long-term modelled illumination fraction; not an hourly sequence')
        save_json(out/'illumination_point.json',illum)
    return {'gcp':gcp,'prp':prp,'illumination':illum}

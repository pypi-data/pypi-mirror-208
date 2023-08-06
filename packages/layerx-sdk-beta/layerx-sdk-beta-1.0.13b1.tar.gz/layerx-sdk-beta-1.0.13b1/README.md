# layerx-python-sdk

LayerX Python API Client
Sync (upload/download) with LayerX stacks via APIs from your local machine

You can
- Upload model runs data


## Installation

`$ pip install layerx-sdk`

## Usage

```python
import layerx  
  
api_key = 'xxxxxxxxxx' 
secret = 'xxxxxxxxxxx'
url = 'https://api.xxxx.layerx.ai'
  
client = layerx.LayerxClient(api_key, secret, url)  

collection_base_path = 'path1/path2/'
  
#upload box type annotations
file_path_bbox = '/home/bob/mydata/example_bbox.json' #local file path
client.upload_modelrun_from_json(collection_base_path, 'test model v1.0.1', file_path_bbox, 'rectangle')

#upload polygon type annotations
file_path_polygon = '/home/bob/mydata/example_polygon.json'
client.upload_modelrun_from_json(collection_base_path, 'test model v1.0.2', file_path_polygon, 'polygon')

#upload line type annotations
file_path_line = '/home/bob/mydata/example_line.json'
client.upload_modelrun_from_json(collection_base_path, 'test model v1.0.3', file_path_line, 'line')
```

## Sample Data

**Box Geometry**
```json
{
   "images":[
      {
         "image":"000000397133.jpg",
         "annotations":[
            {
               "bbox":[
                  217.62,
                  240.54,
                  38.99,
                  57.75
               ],
               "label":"kitchen",
               "metadata":{
                  "name":"bottle"
               },
               "confidence":0.30611335805442985
            }
         ]
      }
   ]
}
```

**Polygon Geometry**
```json
{
   "images":[
      {
         "image":"000000397133.jpg",
         "annotations":[
            {
               "polygon":[
                  [
                     224.24,
                     297.18
                  ],
                  [
                     228.29,
                     297.18
                  ],
                  [
                     234.91,
                     298.29
                  ],
                  [
                     243.0,
                     297.55
                  ],
                  [
                     249.25,
                     296.45
                  ],
                  [
                     252.19,
                     294.98
                  ],
                  [
                     256.61,
                     292.4
                  ],
                  [
                     254.4,
                     264.08
                  ],
                  [
                     251.83,
                     262.61
                  ],
                  [
                     241.53,
                     260.04
                  ],
                  [
                     235.27,
                     259.67
                  ],
                  [
                     230.49,
                     259.67
                  ],
                  [
                     233.44,
                     255.25
                  ],
                  [
                     237.48,
                     250.47
                  ],
                  [
                     237.85,
                     243.85
                  ],
                  [
                     237.11,
                     240.54
                  ],
                  [
                     234.17,
                     242.01
                  ],
                  [
                     228.65,
                     249.37
                  ],
                  [
                     224.24,
                     255.62
                  ],
                  [
                     220.93,
                     262.61
                  ],
                  [
                     218.36,
                     267.39
                  ],
                  [
                     217.62,
                     268.5
                  ],
                  [
                     218.72,
                     295.71
                  ],
                  [
                     225.34,
                     297.55
                  ]
               ],
               "label":"kitchen",
               "metadata":{
                  "name":"bottle"
               },
               "confidence":0.8316836170368476
            }
         ]
      }
   ]
}
```

**Line Geometry**
```json
{
   "images":[
      {
         "image":"000000397133.jpg",
         "annotations":[
            {
               "line":[
                  [
                     217.62,
                     240.54
                  ],
                  [
                     256.61,
                     240.54
                  ],
                  [
                     256.61,
                     298.28999999999996
                  ],
                  [
                     217.62,
                     298.28999999999996
                  ]
               ],
               "label":"kitchen",
               "metadata":{
                  "name":"bottle"
               },
               "confidence":0.9496247739008129
            }
         ]
      }
   ]
}
```

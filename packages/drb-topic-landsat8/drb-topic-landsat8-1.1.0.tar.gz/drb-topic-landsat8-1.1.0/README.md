# DRB Topic Landsat 8
Topic plugin for DRB Python, this project define
[Landsat8](https://www.usgs.gov/landsat-missions/landsat-8) data.

More details about DRB: https://drb-python.gitlab.io/drb/user/what_is_drb.html

## Installation
``` shell
pip install drb-topic-landsat8
```

## Landsat 8 topics
```mermaid
graph BT
    A([Landsat-8 Level-1 GeoTIFF Product<br/>d6ec274f-d84a-499d-923a-5116c1b96655])
    B([Landsat-8 Level-1 GeoTIFF Collection 1 Product<br/>10e14810-3060-4f55-99e7-3a84e2947343])
    C([Landsat-8 Level-1 GeoTIFF Collection 2 Product<br/>460f7ffa-3ebb-4122-8ce3-53d54432727b])
    D([Landsat-8 Level-1 Metadata Text File<br/>b299117e-123b-482e-869f-ddb085677952])

    B & C --> A
    D
```

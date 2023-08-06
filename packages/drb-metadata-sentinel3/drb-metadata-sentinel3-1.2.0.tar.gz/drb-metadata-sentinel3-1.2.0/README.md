# DRB Metadata Sentinel 3
This DRB addon allowing to extract metadata of *Sentinel-3* products.

see:
 - [Sentinel-3](https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-3)
 - [drb-topic-sentinel3](https://gitlab.com/drb-python/topics/sentinel3)
## Installation
```
pip install drb-metadata-sentinel3
```
## Examples
```python
from drb.factory import DrbFactoryResolver
from drb_metadata import DrbMetadataResolver

path = 'S3B_SR_2_LAN____20220903T105648_20220903T114717_20220905T050748_3029_070_094______PS2_O_ST_004.SEN3'
node = DrbFactoryResolver().create(path)
metadata_dict = DrbMetadataResolver().get_metadata(node)
for name, metadata in metadata_dict.items():
    print(f'{name} --> {metadata.extract(node)}')
```

## Metadata
Following subsection define lists of metadata can be extract from Sentinel-3
products via the drb-metadata-sentinel3.

### Common
Common metadata names to all Sentinel-3 products.

| Name                     |
|:-------------------------|
| platformShortName        |
| platformSerialIdentifier |
| processingCenter         |
| processorName            |
| processorVersion         |
| beginningDateTime        |
| endingDateTime           |
| productType              |
| timeliness               |
| baselineCollection       |

### Sentinel-3 Level 0 Products
| Name                | MWR     | SRAL    | SLSTR   | OLCI    | GNSS    | DORIS   | NAVATT  | HKTMs   |
|:--------------------|:--------|:--------|:--------|:--------|:--------|:--------|:--------|:--------|
| operationalMode     | &check; | &check; | &check; | &check; | &check; | &check; | &check; | &check; |
| instrumentShortName | &check; | &check; | &check; | &check; | &check; | &check; | &check; | &check; |
| processingDate      | &check; | &check; | &check; | &check; | &check; | &check; | &check; | &check; |
| orbitNumber         | &check; | &check; | &check; | &check; | &check; | &check; | &check; | &check; |
| relativeOrbitNumber | &check; | &check; | &check; | &check; | &check; | &check; | &check; | &check; |
| orbitDirection      | &check; | &check; | &check; | &check; | &check; | &check; | &check; | &check; |
| cycleNumber         | &check; | &check; | &check; | &check; | &check; | &check; | &check; | &check; |
| coordinates         | &check; | &check; | &check; | &check; | &check; | &check; | &check; | &check; |
| tileId              | &check; | &check; | &check; | &check; | &check; | &check; | &check; | &check; |

### Sentinel-3 Level 1 Products
| Name                      | MWR     | SRAL    | SLSTR   | OLCI    | SYNERGY |
|:--------------------------|:--------|:--------|:--------|:--------|:--------|
| operationalMode           | &check; | &check; | &check; | &check; | &check; |
| instrumentShortName       | &check; | &check; | &check; | &check; | &check; |
| processingLevel           | &check; | &check; | &check; | &check; | &check; |
| processingDate            | &check; | &check; | &check; | &check; | &check; |
| orbitNumber               | &check; | &check; | &check; | &check; | &check; |
| relativeOrbitNumber       | &check; | &check; | &check; | &check; | &check; |
| orbitDirection            | &check; | &check; | &check; | &check; | &check; |
| cycleNumber               | &check; | &check; | &check; | &check; | &check; |
| coordinates               | &check; | &check; | &check; | &check; | &check; |
| tileId                    | &check; | &check; | &check; | &check; | &check; |
| landCover                 | &empty; | &check; | &empty; | &empty; | &empty; |
| closeSeaCover             | &empty; | &check; | &empty; | &empty; | &empty; |
| continentalIceCover       | &empty; | &check; | &empty; | &empty; | &empty; |
| openOceanCover            | &empty; | &check; | &empty; | &empty; | &empty; |
| brightCover               | &empty; | &check; | &empty; | &empty; | &empty; |
| cloudCover                | &empty; | &empty; | &check; | &empty; | &empty; |
| salineWaterCover          | &empty; | &empty; | &check; | &check; | &check; |
| landCover                 | &empty; | &empty; | &check; | &empty; | &check; |
| coastalCover              | &empty; | &empty; | &check; | &check; | &check; |
| freshInlandWaterCovertage | &empty; | &empty; | &check; | &check; | &check; |
| tidalRegionCover          | &empty; | &empty; | &check; | &check; | &check; |

### Sentinel-3 Level 2 Products
| Name                      | SRAL    | SLSTR   | OLCI    | SYNERGY |
|:--------------------------|:--------|:--------|:--------|:--------|
| operationalMode           | &check; | &check; | &check; | &check; |
| instrumentShortName       | &check; | &check; | &check; | &check; |
| processingLevel           | &check; | &check; | &check; | &check; |
| processingDate            | &check; | &check; | &check; | &check; |
| orbitNumber               | &check; | &check; | &check; | &check; |
| relativeOrbitNumber       | &check; | &check; | &check; | &check; |
| orbitDirection            | &check; | &check; | &check; | &check; |
| cycleNumber               | &check; | &check; | &check; | &check; |
| coordinates               | &check; | &check; | &check; | &check; |
| tileId                    | &check; | &check; | &check; | &check; |
| landCover                 | &check; | &empty; | &empty; | &empty; |
| closeSeaCover             | &check; | &empty; | &empty; | &empty; |
| continentalIceCover       | &check; | &empty; | &empty; | &empty; |
| openOceanCover            | &check; | &empty; | &empty; | &empty; |
| cloudCover                | &empty; | &check; | &check; | &empty; |
| salineWaterCover          | &empty; | &check; | &check; | &check; |
| landCover                 | &empty; | &check; | &check; | &check; |
| coastalCover              | &empty; | &check; | &check; | &check; |
| freshInlandWaterCovertage | &empty; | &check; | &check; | &check; |
| tidalRegionCover          | &empty; | &check; | &check; | &check; |
| snowOrIceCover            | &empty; | &empty; | &empty; | &check; |

### Sentinel-3 Auxiliary Product
This section contains extractable metadata for Sentinel-3 auxiliary products.

| Name                     |
|:-------------------------|
| platformShorName         |
| platformSerialIdentifier |
| processingCenter         |
| processorName            |
| processorVersion         |
| beginningDateTime        |
| endingDateTime           |
| productType              |
| timeliness               |
| baselineCollection       |
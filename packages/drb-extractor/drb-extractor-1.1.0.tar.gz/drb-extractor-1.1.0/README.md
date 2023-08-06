# DRB Extractor

### Extractor
An extractor as its name suggests allowing to extract information/data from
a node. An extractor is defined by a YAML content. Three extractor types exists
currently:

#### Constant
This extractor nothing from the node but give always the same value.

````yaml
constant: 42
````
Some string values are automatically converted to a specific Python type:

| Value                      | Python type       |
|----------------------------|-------------------|
| 2022-01-01                 | datatime.date     |
| 2022-01-01T00:00:00.000Z   | datatime.datetime |

#### XQuery
This extractor allowing to extract data from the node via an XQuery script.
See more details about [XQuery](https://www.w3.org/TR/xquery-31/).

```yaml
xquery: |
  data(./manifest.safe/XFDU/metadataSection/
  metadataObject[@ID="generalProductInformation"]/metadataWrap/xmlData/
    *[matches(name(),"standAloneProductInformation|generalProductInformation")]/
    noiseCompressionType)
```

#### Python
The Python extractor allowing to extract data from a node via a Python script.
Where the `node` variable represents the current node.

```yaml
python: |
  return node['DATASTRIP'][0]['MTD_DS.xml']['Level-1C_DataStrip_ID']
      ['General_Info']['Datatake_Info'].get_attribute('datatakeIdentifier')
```

#### Script
The Script extractor allowing to extract data from a node via a Python method.
A DrbNode given in argument of the extract method will be put in argument.

```yaml
script: package.module:function1 # execute complex python script to generate the preview
```

example:
```yaml
drbItemClass: aff2191f-5b06-4121-a9fa-f3d93f6c6331
variables:
  - name: node_platform
    xquery: |
      ./manifest.safe/XFDU/metadataSection/metadataObject[@ID="platform"]/
        metadataWrap/xmlData/platform
metadata:
  - name: 'platformName'
    constant: 'Sentinel-1'
  - name: 'SatelliteNumber'
    xquery: |
      declare variable $node_platform external;
      data($node_platform/number)
  - name: 'platformIdentifier'
    python: |
      return node_platform['nssdcIdentifier'].value
  - name: 'resolutionDetail'
    python: |
      resolution = node.name[10:11]
      if resolution == 'F':
        return 'Full'
      elif resolution == 'H':
        return 'High'
      elif resolution == 'M':
        return 'Medium'
      return None
  - name: 'index_340_380'
    script: package.module:function1
```


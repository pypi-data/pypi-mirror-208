# PyECL
SDKs and example code for accessing the Constellation APIs that power Emerald Cloud Lab.

## The constellation API
Detailed documentation about the Constellation API can be found at www.emeraldcloudlab.com/internal-developers-api.

## Quick start
Install with pip:

```
pip install pyecl
```

To use the SDK:
``` python
>>> from pyecl import Constellation
>>> from pyecl.models import Object
>>> client = Constellation()
```

To login:
``` python
>>> client.login("scientist@science.com", "myAwesomePassword")
```

To get information about the current user once you are logged in:
``` python
>>> me = client.me()
>>> print(me)
{'Email': 'scientist@science.com', 'EmailAddress':'scientist@science.com', 'Id': 'id:abc123', 'Type': 'Object.User', 'Username': 'scientist'}
```

To download information from an object:
``` python
>>> client.download(Object(me["Id"]), ["Name", "Email"])
["scientist", "scientist@science.com"]
```

To search for objects of a specific type:
``` python
>>> client.search("Object.Data.Chromatography", "")
```

## Downloading data

You may perform a simple single field download like:
``` python
>>> client.download(Object("id:BYDOjvG4l3Ol"), "ColumnOrientation")
'Forward'
```

You may download multiple fields in a single download like:
``` python
>>> client.download(Object("id:BYDOjvG4l3Ol"), ["SeparationMode", "ColumnOrientation"])
['ReversePhase', 'Forward']
```

You may download from multiple objects in a single download like:
``` python
>>> client.download([Object("id:o1k9jAkRM794"), Object("id:L8kPEjkw47jw")], "ColumnOrientation")
['Forward', 'Forward']
```

And finally, you may download multiple fields from multiple objects in a single download like:
``` python
>>> client.download([Object("id:o1k9jAkRM794"), Object("id:L8kPEjkw47jw")], ["SeparationMode", "ColumnOrientation"])
[['ReversePhase', 'Forward'], ['ReversePhase', 'Forward']]
```

You may also traverse links within downloads, like:
``` python
>>> client.download(Object("id:BYDOjvG4l3Ol"), "Instrument[Model[Name]]")
'Waters Acquity UPLC H-Class ELS with Pre-Column Heater'
```

You can also download all of the fields on an object by not specifying a field.  For example:
``` python
>>> client.download(Object("id:Z1lqpMzvkGMV"))
{'type': 'Object.User.Emerald.Developer', 'id': 'id:Z1lqpMzvkGMV'....}
```

Or via the "All" implicit field:
``` python
>>> client.download(Object("id:Z1lqpMzvkGMV"), "All")
{'type': 'Object.User.Emerald.Developer', 'id': 'id:Z1lqpMzvkGMV'....}
```

Note that in this case, the results will be a dictionary mapping field name to field value

## Dealing with types

There are a number of different ways to interpret field values based off the type of data stored in the object.  String, integer, and real fields are mapped to their corresponding python types - for example:
``` python
>>> client.download(Object("id:BYDOjvG4l3Ol"), ["SeparationMode", "InjectionIndex"])
['ReversePhase', 28]
```

Link fields will return objects, which you can chain downloads off of (although note that traversals will be much faster):
``` python
>>> client.download(Object("id:BYDOjvG4l3Ol"), "Instrument")
Object[Instrument[HPLC, "id:wqW9BP4ARZVw"]
>>> client.download(client.download(Object("id:BYDOjvG4l3Ol"), "Instrument"), "Name")
'Galadriel'
>>> client.download(Object("id:BYDOjvG4l3Ol"), "Instrument[Name]")
'Galadriel'
```

Date fields will be converted to native python datetime objects:
``` python
>>> client.download(Object("id:BYDOjvG4l3Ol"), "DateCreated")
datetime.datetime(2022, 1, 9, 23, 44, 31, 746154)
```

Quantity arrays will be converted to python variable unit objects:
``` python
>>> client.download(Object("id:BYDOjvG4l3Ol"), "Scattering")                                                                                          
[[0.0 Minutes, -87.528984 IndependentUnit[Lsus]], [0.016667 Minutes, -96.701614 IndependentUnit[Lsus]], [0.033333 Minutes, -43.93272 IndependentUnit[Lsus]], [0.05 Minutes, -132.207855 IndependentUnit[Lsus]]...
```

which you may manipulate to get their values and units:
``` python
>>> scattering_info = client.download(Object("id:BYDOjvG4l3Ol"), "Scattering")
>>> len(scattering_info)
361
>>> scattering_info[0]
[0.0 Minutes, -87.528984 IndependentUnit[Lsus]]
>>> scattering_info[0][0]
0.0 Minutes
>>> scattering_info[0][0].value
0.0
>>> scattering_info[0][0].unit
'Minutes'
```

Blob refs will be downloaded and automatically parsed in the same way:
```python
>>> client.download(Object("id:BYDOjvG4l3Ol"), "Absorbance")
[[0.0 'Minutes', 0.0 'Milli' 'AbsorbanceUnit'], [0.0008333333535119891 'Minutes', 0.0 'Milli' 'AbsorbanceUnit']...
```

Additionally, you can download multiple fields that have different units the same as you would download other fields.  For example:
```python
>>> client.download(Object("id:O81aEB16GlJ1"), "Composition")
[[4.977777777777776 Times[Power["Liters", -1], "Milligrams"], Object[Model[Molecule, "id:E8zoYvN6m61A"]], [75.11111111111111 IndependentUnit["VolumePercent"], Object[Model[Molecule, "id:vXl9j57PmP5D"]]]
```

Finally, you can download association fields and they will be automatically translated into python structures.  For example:

```python
>>> client.download(Object("id:XnlV5jKZwmp3"), "ResolvedOptions")['Instrument']
Object[Instrument[HPLC, "id:wqW9BP4ARZVw"]
```

## Download Files

Files are controlled via the `auto_download_cloud_files` flag to the download function.  By default, they will be returned as objects and not downloaded.

For example:
```python
>>> client.download(Object("id:BYDOjvG4l3Ol"), "DataFile")
Object[EmeraldCloudFile, "id:9RdZXv1jDAZ6"]
````

These may be manually downloaded via:
```python
>>> client.download_cloud_file(client.download(Object("id:BYDOjvG4l3Ol"), "DataFile"))
'/var/folders/j_/ftdn14ms37s40j2z0h1wzxbw0000gn/T/tmp6krhb8lp/Absorbance Raw File.bin_absorbancefile'
```

or, it is possible to automatically download them by using the `auto_download_cloud_files` flag of download:
```python
>>> data_file = client.download(Object("id:BYDOjvG4l3Ol"), "DataFile", auto_download_cloud_files=True)
>>> data_file.local_path
'/var/folders/j_/ftdn14ms37s40j2z0h1wzxbw0000gn/T/tmp6krhb8lp/Absorbance Raw File_1.bin_absorbancefile'
```

The format of these files can often change, but the sdk is pretty smart about interpreting them.  Once you have downloaded
the file, you can have the sdk attempt to parse it into python structs via the following:

```python
>>> data_file = client.download(Object("id:BYDOjvG4l3Ol"), "DataFile", auto_download_cloud_files=True)
>>> from constellation_field_parser import ConstellationFieldParser
>>> ConstellationFieldParser().parse_local_file(data_file.local_path)
[[0.0 'Minutes', 273.0 'Nanometers', 0.0 'Milli' 'AbsorbanceUnit'], [0.0008333333535119891 'Minutes', 273.0 'Nanometers', 0.0 'Milli' 'AbsorbanceUnit']...
```

If the field parser is unable to parse the file, it will return `None`.

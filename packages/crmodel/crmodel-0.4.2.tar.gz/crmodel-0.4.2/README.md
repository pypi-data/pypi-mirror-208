# crmodel

**crmodel** is a python package that produces the crossroadsdesriber model from an OpenStreetMap intersection. See [this publication](doi.org/10.5194/agile-giss-3-40-2022) for further informations.

This tool was developed and tested under Ubuntu 20.04.

## Dependencies

This tool mainly depends on [crseg](https://github.com/jmtrivial/crossroads-segmentation) for the intersection segmentation. All necessary Python libraries can be installed with pip:

```bash
pip3 install -r requirements.txt
````

## How to use

You can obtain the model of an intersection this way :

```bash
./main -c x y -o output.format
````
With **x** and **y** the coordinates of the targeted intersection. The output will depend on the format precised. Two formats are supported :

* **json** will give a "raw" output of the model with all classes and attributes.
* **geojson** will give the intersection as segmented by [crseg](https://github.com/jmtrivial/crossroads-segmentation) as a geojson file, complemented with computed elements from crmodel as attributes (ordered branches, islands, sidewalks, crossings, etc.).
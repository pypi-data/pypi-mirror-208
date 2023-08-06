# gds3xtrude
A simple layout to 3D converter.

gds3xtrude takes the layers of your layout and converts them into 3D volumes by extrusion.

`gds3xtrude` is intended to be used in two different ways:
* as KLayout extension: Show 3D model of the active view.
* as standalone tool: Convert GDS to OpenSCAD/Blender from the command line.

![Screenshot](./examples/freepdk45_screenshot.png "Screenshot")

## Dependencies
* OpenSCAD: 3D modelling tool. Can be installed using the package manager of most linux distributions.
* solidpython: Python library for creating OpenSCAD models.
* klayout: Python module of KLayout used for GDS input/output and polygon operations.

## Install (Linux)

### As KLayout package
Use the KLayout package manager to install `gds3xtrude`.
Dependencies (gds3xtrude python package, OpenSCAD) must be installed manually:

```sh
apt install openscad
pip3 install --user gds3xtrude[standalone]
```

### As standalone tool
When used as a standalone tool `gds3xtrude` additionally depends on the klayout Python package.

```sh
pip3 install --user gds3xtrude
pip3 install --user klayout
```

### Install from Git (instead of installing using pip)
```sh
git clone [this repo]
cd gds3xtrude
pip install --user .
```

## Install (Windows)
Windows is currently not supported but very likely you can get gds3xtrude running there with some tweaks.
Here are some ideas how to install it:
* Install Python and pip
* Get OpenSCAD: http://www.openscad.org/downloads.html
* Rest should be similar to the Linux install instructions.

## Usage

### As KLayout module

* Open a layout.
* Zoom in to the region you want to pass to gds3xtrude.
* Select `Tools -> gds3xtrude -> run script`
* Select the layerstack file for your technology. (Example for FreePDK45 can be found in `examples/freepdk45.layerstack`)


### As standalone tool
Example usage:
```sh
# Get layerstack file for FreePDK45.
wget https://codeberg.org/tok/gds3xtrude/raw/branch/master/examples/freepdk45.layerstack

# Get a GDS file.
wget https://codeberg.org/tok/gds3xtrude/raw/branch/master/examples/NAND2X1.gds

# Run gds3xtrude
gds3xtrude --tech freepdk45.layerstack --input NAND2X1.gds --view
```

If you get an error like `gds3xtrude: command not found` the program is probably not in your `PATH` environment variable.
Try to add the pip binary directory to the PATH variable first:
```sh
PATH=$PATH:$HOME/.local/bin
# And now again: gds3xtrude ...
```

### Layer stack definition
To convert a 2D layout into a 3D model some information about the physical layer stack is necessary.
This information must be passed to gds3xtrude as a file. An example of a simple layer stack description
for the FreePDK45 can be found in `examples/freepdk45.layerstack`. Use this file as a starting point and adapt it to your needs.

Essentially a layerstack file is just a python script that defines some data structures.

Example:
```python
from gds3xtrude.include import layer, Material

# Define layers
poly = layer(15)
contact = layer(16)
metal1 = layer(21)

# Define materials and colors
m_poly = Material('poly', color=(0.8, 0.2, 0.2))
m_metal1 = Material('metal1', color=(0.8, 0.2, 0.2))

# Assign materials
poly.material = m_poly
metal1.material = m_metal1

# Define additional layers from boolean operation
contact_to_silicon = contact - poly

# Define layer stack structure as a list of `(layer thickness, [masks, ...])`.
# and/or `([mask, ...], z_start, z_end)`.
# The 3D model is created layer by layer from bottom to top.
layerstack = [
    (10, contact_to_silicon), # Start at 0 and create a slice of thickness 10.
    (20, [contact, poly]), # Put a slice of thickness 20 on top of the previous slice.
    (50, contact), # Put a slice of thickness 5 on top of the previous slice.
    (50, metal1),

    # You can also use absolute z-coordinates by using the following syntax:
    (metal1, 200, 220), # Create a slice from z=200 to z=220 based on the metal1 mask.
]
```

The crossection of the layer stack described in the example above is shown here. Note that the contact from metal1 down to silicon (which is not shown nor included in the example) consists of three parts. This is only due to the layer by layer creation of the 3D model but it is important to understand for writing the layerstack definition. For instance on the lowest layer there is only a piece of contact down to silicon. Contacts wich have polysilicon below do not reach this lowest layer. This is modelled as the boolean difference `contact_to_silicon = contact - poly`.
Masks can be merged by putting them into a list as used for the second layer (`[contact, poly]`).

![layer stack illustration](./doc/layerstack_doc.png "layer stack")

## Blender
3D models can also be generated in blender. Use the command line tool for this:
```sh
gds3xtrude --tech freepdk45.layerstack --input NAND2X1.gds --cad blender
```
Note that the current implementation over the Blender scripting API is very slow and therefore only small things such as standard cells can be visualized.
Also make sure to use Blender 2.82 or higher.

## FreeCAD
The generated OpenSCAD models (.scad) can be imported into FreeCAD.

### Color Issue
When applying a boolean union FreeCAD strips away colors. Therefore an exported .obj model will by totally gray. There is a workaround:
* Open the OpenSCAD model in FreeCAD
* Open the `Model` tab in `Combo View`
* Expand the list of the imported model which is likely to be named `Unnamed`
* Find a child node labelled `union`, select and delete it
* Select the full model to be exported (Ctrl-A)
* Now you can export to .obj without loosing color information

Additionally to the .obj file FreeCAD will also create a .mtl file containing material/color information. Blender will automatically read it when importing the .obj file.

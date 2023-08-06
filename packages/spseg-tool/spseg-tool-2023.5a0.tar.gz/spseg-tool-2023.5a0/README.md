# SP-SEG: Proof of concept tool for manual segmentation by spheripixel projection
In this repository, you can find a proof of concept of the tool for manual point cloud labeling by spherical point-pixel projection.

## ❗ Limitations
The current version is just the proof of concept version.

## 🔧 Environment and installation
```python
python >= 3.10
```
Required packages:
```python
"PyQt5",
"Pillow",
"numpy",
"pydantic",
"scikit-learn",
"scipy",
"colormath",
"tqdm",
"toml"
```

To install the software:
1. Clone the repository and run inside:
```bash
pip install .
```
1. Or use:
```bash
pip install sp-seg
```

> If you're experiencing issues with installing the package, install firstly the dependencies:
> ```bash
> pip install PyQt5 Pillow numpy pydantic scikit-learn scipy colormath tqdm toml
> ```

Then, you can run the software with the command:
```bash
D:\>spseg
```


## 📖 Instruction
The main view of the software looks like the following:

1. [Starting the application](#starting-the-application)
1. [Opening point cloud](#opening-a-point-cloud)
1. [Loading labels definition](#loading-labels-definition)
1. [Zooming in and out](#zooming-in-and-out)
1. [Depth preview](#depth-preview)
1. [Depth scale](#depth-scale)
1. [Vertical roll](#vertical-roll)
1. [Horizontal roll](#horizontal-roll)
1. [Object segentation](#object-segmentation)
1. [Deselecting region](#deselecting-region)
1. [Changing mask opacity](#changing-mask-opacity)
1. [Accepting an object](#accepting-an-object)
1. [Saving segmentation result](#saving-segmentation-result)


### Starting the application
Having installed the application, just run the following command in the command line:
```bash
D:\>spseg
```
### Opening a point cloud
To open a point cloud, click `Open` icon in the toolbar and choose a proper file.
> ❗ At the moment only PTS files are supported 

> ❗ If you need to change the columns meaning of PTS opener, modify the `opener.column` key of the config file. Currently interpretable letters are `X`, `Y`, `Z`, `R`, `G`, and `B`

![](gifs/open_cloud.gif)


### Loading labels definition
To open labels click the proper icon in the toolbar and choose the JSON file with labels definitions.
Example labels definition may look like below:

```json
[
  {
    "label": "ceiling",
    "code": 0,
    "color": [4, 255, 0]
  },
  {
    "label": "floor",
    "code": 1,
    "color": [255, 128, 0]
  }
]
```

![](gifs/open_labels.gif)


### Zooming in and out
For easier detail selection you can zoom in and zoom out. To do so keep `Ctrl` pressed and use mouse wheel.
![](gifs/zoom.gif)


### Depth preview
Sometimes, it may be useful to get insight into depth distribution. To see the depth map, just press `Alt` button.
![](gifs/depth.gif)

### Depth scale
To change $\gamma$ of the depth map, use `+` or `-` buttons while `Alt` is pressed.
![](gifs/depth_scale.gif)


### Vertical roll
To roll the scene vertically, press `Q` button.
![](gifs/roll_vert.gif)


### Horizontal roll
To roll the scene horizontally, press `W` button.
![](gifs/roll_hor.gif)

### Object segmentation
To segment an object, choose the proper category in the menu of the left and start selecting the polygon.
To add a vertex to the polygon, use left mouse button. If you want to close a polygon, click right mouse button.

> ❗ Closing polygon creates an edge between the first and the last added vertex!

> ❗ You don't need to select the entire object using a single polygon. You can draw as many polygons for an object as you wish, until the object segmentation will be accepted by pressing `F1` button.

![](gifs/select.gif)

### Deselecting region
You can deselect fragments of scene selected by mistake. To do so, check the mode to `Deselect` (radio button in the tollbar) or use `Caps Lock` button.
For deselecting you also draws a polygon.

> ❗ Remember to change the mode to `Select` when you already deselected the desired points.

![](gifs/deselect.gif)

### Changing mask opacity

To change the opacity of the mask of currently segmented object, use the slider just below the toolbar.
![](gifs/transparency.gif)


### Accepting an object
When you finish the object segmentation you need to accept the instance of the category by clicking `F1` button.
![](gifs/save_obj.gif)


### Saving segmentation result
To save the PTS result, choose the proper icon in the toolbar menu.
![](gifs/save_cloud.gif)


## 🏎️ Further development
- [ ] code optimization
- [ ] code cleaning
- [ ] add handling other point cloud formats
- [ ] handle non-single-setup point clouds
- [ ] enable saving draft segmentation result


## 📝 Citation

```bibtex
@ONLINE{sp-seg,
  author = {Walczak, J., Osuch, A., Wojciechowski, A.},
  title = {{SP-SEG}: Proof of concept tool for manual segmentation by spheripixel projection},
  year = 2023,
  url = {https://github.com/jamesWalczak/sp-seg-tool},
  urldate = {<access date here>}
}
```

## ⚖️ 3rd party attribution
<b>Icons attribution:</b> <a href='https://www.flaticon.com/free-icons/save' title='save icons'>Save icons created by Freepik - Flaticon</a>
<br/>
<b>Animation attribution:</b> Animation generated from <a href='https://icons8.com'>Icons8</a>

## 🎁 Ackowledgement
This software was developed as a part of the research project "Semantic analysis of 3D point clouds", co-funded by the Polish National Center for Research and Development under the LIDER XI program [grant number 0092/L-11/2019]. 
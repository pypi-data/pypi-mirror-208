# Welcome to organelle_segmenter_plugin
🚧 WIP 🚧

For full documentation visit [ndcn.github.io/organelle-segmenter-plugin](https://ndcn.github.io/organelle-segmenter-plugin/)
This plugin that enables image segmentation of organelles from linearly-unmixed florescence images based on the segmenter tools provided by Allen Institute for Cell Science.  This fork is NOT a 3D (volumetric) segmentation at this time.  Instead it is a proof-of-concept which infers an "best" Z-slice / Z-projection and performes a 2D analysis.

This plugin is designed to work with [infer-subc](https://github.com/ergonyc/infer-subc) and [aics-segmenter]( https://allencell.org/segmenter )

## GOAL
To measure shape, position, size, and interaction of eight organelles/cellular components (Nuclei (NU), Lysosomes (LS),Mitochondria (MT), Golgi (GL), Peroxisomes (PO), Endoplasmic Reticulum (ER), Lipid Droplet (LD), and SOMA) during differentiation of iPSCs, in order to understand the Interactome / Spatiotemporal coordination.

### Forked from Allen Institute for Cell Science project
The Allen Cell & Structure Segmenter plugin for napari, from which this projects is forked, provides an intuitive graphical user interface to access the powerful segmentation capabilities of an open source 3D segmentation software package developed and maintained by the Allen Institute for Cell Science (classic workflows only with v1.0). ​[The Allen Cell & Structure Segmenter](https://allencell.org/segmenter) is a Python-based open source toolkit developed at the Allen Institute for Cell Science for 3D segmentation of intracellular structures in fluorescence microscope images. This toolkit brings together classic image segmentation and iterative deep learning workflows first to generate initial high-quality 3D intracellular structure segmentations and then to easily curate these results to generate the ground truths for building robust and accurate deep learning models. The toolkit takes advantage of the high replicate 3D live cell image data collected at the Allen Institute for Cell Science of over 30 endogenous fluorescently tagged human induced pluripotent stem cell (hiPSC) lines. Each cell line represents a different intracellular structure with one or more distinct localization patterns within undifferentiated hiPS cells and hiPSC-derived cardiomyocytes.

More details about Segmenter can be found at https://allencell.org/segmenter

----------------------------------


## Installation 🚧 WIP 🚧

### Option 1 (recommended): 🚧 WIP 🚧
`organelle_segmenter_plugin` is  available on `PyPI` via: 

```bash
pip install organelle_segmenter_plugin
```
### Option 2 🚧 COMING SOON 🚧 (not yet available on napari hub)

After you installed the lastest version of napari, you can go to "Plugins" --> "Install/Uninstall Package(s)". Then, you will be able to see all available napari plugins and you can find us by name `organelle-segmenter-plugin`. Just click the "install" button to install the Segmenter plugin.

### Option 3: clone repo + editable install

```bash
git clone https://github.com/ndcn/organelle-segmenter-plugin.git
cd organelle-segmenter-plugin
pip install -e .
```
## OVERVIEW

In the current version, there are two parts in the plugin: **workflow editor** and **batch processing**. The **workflow editor** allows users adjusting parameters in all the existing workflows in the lookup table, so that the workflow can be optimized on users' data. The adjusted workflow can be saved and then applied to a large batch of files using the **batch processing** part of the plugin. 

1. Open a file in napari by dragging multi-channel .czi file onto napari which will import a multi-channel, multi-Z 'layer'. (Using the menu's defaults to `aicsIMAGEIO` reader which automatically splits mutliple channels into individual layers.  The plugin is able to support multi-dimensional data in .tiff, .tif. ome.tif, .ome.tiff, .czi)
2. Start the plugin (open napari, go to "Plugins" --> "organelle-segmenter-plugin" --> "workflow editor")
3. Select the image and channel to work on
4. Select a workflow based on the example image and target segmentation based on user's data. Ideally, it is recommend to start with the example with very similar morphology as user's data.
5. Click "Run All" to execute the whole workflow on the sample data.
6. Adjust the parameters of steps, based on the intermediate results. For instruction on the details on each function and the effect of each parameter, click the tooltip button. A complete list of all functions can be found [here](https://github.com/ndcn/infer-subc/blob/main/infer_subc/organelles_config/function_params.md)
7. Click "Run All" again after adjusting the parameters and repeat step 6 and 7 until the result is satisfactory.
8. Save the workflow
9. Close the plugin and open the **batch processing** part by (go to "Plugins" --> "organelle-segmenter-plugin" --> "batch processing")
10. Load the customized workflow (or an off-the-shelf workflow) json file
11. Load the folder with all the images to process
12. Click "Run"

## `napari` 
**napari** is a fast, interactive, multi-dimensional image viewer for Python. It's designed for browsing, annotating, and analyzing large multi-dimensional images. It's built on top of Qt (for the GUI), vispy (for performant GPU-based rendering), and the scientific Python stack (numpy, scipy). It can be installed via python tools (i.e. `pip` or `conda`) or as a stand-alone gui.  
More info can be found on their [website](https://napari.org/stable/) and at [this repository](https://github.com/napari/napari).

A powerful extension framework of **napari plugins**  extend `napari`s functionality.   More infor can be foudn at the [napari hub](https://www.napari-hub.org/about) The napari hub seeks to solve many of the challenges and needs in finding analysis solutions to bioimaging problems. 

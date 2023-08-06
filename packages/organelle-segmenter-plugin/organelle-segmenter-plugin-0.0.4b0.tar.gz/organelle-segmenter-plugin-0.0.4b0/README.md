# organelle-segmenter-plugin

[![License BSD-3](https://img.shields.io/pypi/l/organelle-segmenter-plugin.svg?color=green)](https://github.com/ergonyc/organelle-segmenter-plugin/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/organelle-segmenter-plugin.svg?color=green)](https://pypi.org/project/organelle-segmenter-plugin)
[![Python Version](https://img.shields.io/pypi/pyversions/organelle-segmenter-plugin.svg?color=green)](https://python.org)
[![tests](https://github.com/ergonyc/organelle-segmenter-plugin/workflows/tests/badge.svg)](https://github.com/ergonyc/organelle-segmenter-plugin/actions)
[![codecov](https://codecov.io/gh/ergonyc/organelle-segmenter-plugin/branch/main/graph/badge.svg)](https://codecov.io/gh/ergonyc/organelle-segmenter-plugin)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/organelle-segmenter-plugin)](https://napari-hub.org/plugins/organelle-segmenter-plugin)

 🚧 WIP 🚧
A plugin that enables image segmentation of organelles from linearly-unmixed florescence images based on the segmenter tools provided by Allen Institute for Cell Science. 

A [napari](https://napari.org/stable/) plugin to infer subcellular components leveraging [infer-subc](https://github.com/ergonyc/infer-subc) and [aics-segmenter]( https://allencell.org/segmenter )

## GOAL
To measure shape, position, size, and interaction of  organelles/cellular components (Nuclei (nuc, NU), Nucleus (N1), Lysosomes (LS), Mitochondria (mito, MT), Golgi (GL), Peroxisomes (perox, PO), Endoplasmic Reticulum (ER), Lipid Droplet (LD), Cellmask (soma, cellmask), and cytoplasm (cyto, CT) ) during differentiation of iPSCs, in order to understand the Interactome / Spatiotemporal coordination.

🚧 WIP 🚧
 
### Forked from Allen Institute for Cell Science project
The Allen Cell & Structure Segmenter plugin for napari, from which this projects is forked, provides an intuitive graphical user interface to access the powerful segmentation capabilities of an open source 3D segmentation software package developed and maintained by the Allen Institute for Cell Science (classic workflows only with v1.0). ​[The Allen Cell & Structure Segmenter](https://allencell.org/segmenter) is a Python-based open source toolkit developed at the Allen Institute for Cell Science for 3D segmentation of intracellular structures in fluorescence microscope images. This toolkit brings together classic image segmentation and iterative deep learning workflows first to generate initial high-quality 3D intracellular structure segmentations and then to easily curate these results to generate the ground truths for building robust and accurate deep learning models. The toolkit takes advantage of the high replicate 3D live cell image data collected at the Allen Institute for Cell Science of over 30 endogenous fluorescently tagged human induced pluripotent stem cell (hiPSC) lines. Each cell line represents a different intracellular structure with one or more distinct localization patterns within undifferentiated hiPS cells and hiPSC-derived cardiomyocytes.

More details about Segmenter can be found at https://allencell.org/segmenter

----------------------------------

This [napari] plugin was generated with [Cookiecutter] using with [@napari]'s [cookiecutter-napari-plugin] template.

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/cookiecutter-napari-plugin#getting-started

and review the napari docs for plugin developers:
https://napari.org/docs/plugins/index.html
-->

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
## Quick Start

In the current version, there are two parts in the plugin: **workflow editor** and **batch processing**. The **workflow editor** allows users adjusting parameters in all the existing workflows in the lookup table, so that the workflow can be optimized on users' data. The adjusted workflow can be saved and then applied to a large batch of files using the **batch processing** part of the plugin. 

1. Open a file in napari by dragging multi-channel .czi file onto napari which will import a multi-channel, multi-Z 'layer'. (Using the menu's defaults to `aicsIMAGEIO` reader which automatically splits mutliple channels into individual layers.  The plugin is able to support multi-dimensional data in .tiff, .tif. ome.tif, .ome.tiff, .czi)
2. Start the plugin (open napari, go to "Plugins" --> "organelle-segmenter-plugin" --> "workflow editor")
3. Select the image and channel to work on
4. Select a workflow based on the example image and target segmentation based on user's data. Ideally, it is recommend to start with the example with very similar morphology as user's data.
5. Click "Run All" to execute the whole workflow on the sample data.
6. Adjust the parameters of steps, based on the intermediate results.  A complete list of all functions can be found [here](https://github.com/ndcn/infer-subc/blob/main/infer_subc/organelles_config/function_params.md)🚧 WIP 🚧
7. Click "Run All" again after adjusting the parameters and repeat step 6 and 7 until the result is satisfactory.
8. Save the workflow
9. Close the plugin and open the **batch processing** part by (go to "Plugins" --> "organelle-segmenter-plugin" --> "batch processing")
10. Load the customized workflow saved above 
11. Load the folder with all the images to process
12. Click "Run"
13. Follow the [examples](https://github.com/ndcn/infer-subc/blob/main/notebooks/14_final_workflow.ipynb) in the `infer_subc` [repo](https://github.com/ndcn/infer-subc/) for postprocessing of the saved segmentations and generating the statistics.  

## Contributing

Contributions are very welcome. 

## License

Distributed under the terms of the [BSD-3] license,
"organelle-segmenter-plugin" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin
[file an issue]: https://github.com/ndcn/organelle-segmenter-plugin/issues
[napari]: https://github.com/napari/napari
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/

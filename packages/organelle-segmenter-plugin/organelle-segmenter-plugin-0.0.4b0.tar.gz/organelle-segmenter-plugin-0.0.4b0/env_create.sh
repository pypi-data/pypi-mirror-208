# bioformats_jar was screwing things up. with OME
conda create -n napari-test python=3.9 pip notebook 
conda activate napari-test 
pip install 'napari[all]'
pip install scipy scikit-learn matplotlib #jupyter
pip install aicsimageio 
pip install aicspylibczi
pip install aicssegmentation #downgrades napari and scikitlearn

pip install napari-aicsimageio  
pip install black
pip install pytest

pip install -e ../infer-subc #infer_subc
pip install -e .

# for ADWB remove the "editable" install

pip install  .<path to infer-subc> #infer_subc
pip install  <path to orgnaelle-segmenter-npe2>


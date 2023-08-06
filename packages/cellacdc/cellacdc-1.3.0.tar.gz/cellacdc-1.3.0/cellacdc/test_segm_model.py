import os
import sys

import matplotlib.pyplot as plt

from importlib import import_module

from cellacdc import apps, myutils, widgets

from PyQt5.QtWidgets import QApplication, QStyleFactory

try:
    import pytest
    pytest.skip('skipping this test since it is gui based', allow_module_level=True)
except Exception as e:
    pass

gdrive_path = myutils.get_gdrive_path()

test_img_path = (
    # os.path.join(
    #    gdrive_path,
    #    *(r'01_Postdoc_HMGU\Python_MyScripts\MIA\Git\DeepSea\data\test_images\A11_z007_c001.png').split('\\'))
    # r"G:\My Drive\01_Postdoc_HMGU\Python_MyScripts\MIA\Git\DeepSea\data\test_images\train_A11_z001_c001.png"
    # r"G:\My Drive\01_Postdoc_HMGU\Python_MyScripts\MIA\Git\Cell_ACDC\data\test_images\test_cellpose.tif"
    os.path.join(
        gdrive_path,
        *(r'01_Postdoc_HMGU\Python_MyScripts\MIA\Git\Cell_ACDC\data\test_images\test_YeaZ.tif').split('\\'))
)

# Ask which model to use --> Test if new model is visible
app = QApplication(sys.argv)
app.setStyle(QStyleFactory.create('Fusion'))

cellacdc_path = os.path.dirname(os.path.abspath(__file__))
models = myutils.get_list_of_models()
win = widgets.QDialogListbox(
    'Select model',
    'Select model to use for segmentation: ',
    models,
    multiSelection=False
)
win.exec_()

if win.cancel:
    sys.exit('Execution aborted')

model_name = win.selectedItemsText[0]
if model_name == 'Automatic thresholding':
    model_name = 'thresholding'
# Check if model needs to be downloaded
downloadWin = apps.downloadModel(model_name, parent=None)
downloadWin.download()

# Load model as a module
acdcSegment = import_module(f'models.{model_name}.acdcSegment')

# Read all models parameters
init_params, segment_params = myutils.getModelArgSpec(acdcSegment)

# Prompt user to enter the model parameters
try:
    url = acdcSegment.url_help()
except AttributeError:
    url = None

win = apps.QDialogModelParams(
    init_params,
    segment_params,
    model_name, url=url)

win.exec_()

# Initialize model
model = acdcSegment.Model(**win.init_kwargs)

# Use model on a test image
import skimage.io

img = skimage.io.imread(test_img_path)
if img.ndim == 3 and (img.shape[-1] == 3 or img.shape[-1] == 4):
    img = skimage.color.rgb2gray(img)

print(img.shape)

lab = model.segment(img, **win.segment2D_kwargs)

print(lab.shape)

if model_name == 'YeastMate':
    cca_df = model.predictCcaState(img)
    print(cca_df)

fig, ax = plt.subplots(1, 2)
ax[0].imshow(img)
ax[1].imshow(lab)
plt.show()

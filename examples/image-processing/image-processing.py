# from https://medium.com/analytics-vidhya/image-processing-with-python-applications-in-machine-learning-17d7aac6bc97
# see also https://scikit-image.org/docs/stable/auto_examples/applications/plot_thresholding.html

import ipdb
import janitor
import pandas_flavor as pf
import pyjviz
import glob, os.path
import pandas as pd
from skimage.io import imread, imshow
from skimage.color import rgb2gray
from skimage.measure import label, regionprops, regionprops_table
from skimage.filters import threshold_otsu
from skimage.morphology import area_closing, area_opening
import numpy as np

# NB:
# apply overload causes problems in printing of dataframes
# so it is included here to make nested call visualization work
old_apply = pd.Series.apply
@pf.register_series_method
def apply(s: pd.Series, func) -> pd.Series:
    ret = old_apply(s, func)
    return ret

@pf.register_series_method
def load_images(file_pathes: pd.Series) -> pd.DataFrame:
    #ipdb.set_trace()
    df = pd.DataFrame()
    for file_path in file_pathes:
        x_image = imread(file_path)
        im_name = os.path.basename(file_path)
        df = df.append({'im_name': im_name, 'image': x_image}, ignore_index = True)

    aux_df = pd.DataFrame(df.im_name)
    aux_df['file_path'] = file_pathes
    aux_df['file_size'] = aux_df.file_path.apply(lambda x: os.stat(x).st_size)
    #print(aux_df)
    pyjviz.show_obj('<im-file-sizes>', aux_df)
    
    return df

@pf.register_dataframe_method
def subplot(df: pd.DataFrame, *, image_col, title_col, title):
    return df

@pf.register_dataframe_method
def binarize_images(df: pd.DataFrame, thresholding_method) -> pd.DataFrame:
    df['gray_leaf'] = df.image.apply(rgb2gray)
    df['binarized'] = None
    for t in df.itertuples():
        thresh = thresholding_method(t.gray_leaf)
        df.at[t.Index, 'binarized'] = (t.gray_leaf < thresh)
    return df

@pf.register_dataframe_method
def morphology(df: pd.DataFrame) -> pd.DataFrame:
    df['closed'] = df.binarized.apply(area_closing)
    df['opened'] = df.closed.apply(area_opening)
    return df

@pf.register_dataframe_method
def labeling(df):
    df['label_im'] = df.opened.apply(label)
    df['regions'] = df.label_im.apply(regionprops)
    return df

@pf.register_dataframe_method
def get_properties_of_each_region(df: pd.DataFrame) -> pd.DataFrame:
    properties = ['area','convex_area','bbox_area',
                  'major_axis_length', 'minor_axis_length',
                  'perimeter', 'equivalent_diameter',
                  'mean_intensity', 'solidity', 'eccentricity']
    res_df = []
    for t in df.itertuples():
        #ipdb.set_trace()
        p_df = pd.DataFrame(regionprops_table(t.label_im, t.gray_leaf, properties=properties))
        p_df = p_df[(p_df.index != 0) & (p_df.area > 100)]
        p_df['im_name'] = t.im_name
        res_df.append(p_df)
    return pd.concat(res_df)

@pf.register_dataframe_method
def apply_feature_engeneering(df: pd.DataFrame) -> pd.DataFrame:
    df['ratio_length'] = (df['major_axis_length'] / df['minor_axis_length'])
    df['perimeter_ratio_major'] = (df['perimeter'] / df['major_axis_length'])
    df['perimeter_ratio_minor'] = (df['perimeter'] / df['minor_axis_length'])
    df['area_ratio_convex'] = df['area'] / df['convex_area']
    df['area_ratio_bbox'] = df['area'] / df['bbox_area']
    df['peri_over_dia'] = df['perimeter'] / df['equivalent_diameter']
    final_df = df[df.drop('type', axis=1).columns].astype(float)
    final_df = final_df.replace(np.inf, 0)
    final_df['type'] = df['type']
    return final_df

file_pathes = pd.Series(glob.glob("dataset/*.jpg"))

with pyjviz.CB("initial-phase") as cc:
    initial_phase_df = (file_pathes
                        .load_images()#.subplot(image_col = 'image', title_col = 'im_name', title = '(Original Image by Gino Borja, AIM)')
                        .binarize_images(threshold_otsu)#.subplot(image_col = 'binarized', title_col = file_pathes, title = 'binarized')
                        .morphology()#.subplot(image_col = 'opened', title_col = file_pathes, title = 'opened')
                        .labeling()#.subplot(image_col = 'label_im', title_col = file_pathes, title = 'labeled')
                        )
if 1:    
    with pyjviz.CB("build-features"):
        final_df = (initial_phase_df
                    .get_properties_of_each_region()
                    .assign(type = lambda x: x.im_name.apply(lambda x: x.split('.')[0]))
                    .drop(columns = 'im_name')
                    .apply_feature_engeneering()
                    )

pyjviz.save_dot(vertical = True)


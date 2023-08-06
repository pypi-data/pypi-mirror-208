import os
import numpy as np
import pandas as pd
import itertools
from scipy.stats import pearsonr
import seaborn as sns
import matplotlib.pyplot as plt
import glob
import pathlib
from collections import OrderedDict

from general_utility import unique_colors


# pearson coeffcient clustermap of color groups within the csv (single slide hence there will be 1 colortrack)
# takes in directory with a dump of all the k<k_val> csv's
def create_correlation_clustermap_single_slide(dir):
    for fp in glob.glob(os.path.join(dir, '*k[0-9].csv')):
        slide_name, kval = pathlib.Path(fp).stem.rsplit('_', 1)

        df = pd.read_csv(os.path.join(dir, f'{slide_name}_{kval}.csv'))

        colors = list(df['Cluster_color_name'].unique())

        df_corr = pd.DataFrame(np.zeros((len(colors), len(colors))))
        df_corr.columns = colors
        df_corr.index = colors

        for (c1, c2) in itertools.combinations(colors, 2):
            df1 = df[df['Cluster_color_name'] == c1]
            df2 = df[df['Cluster_color_name'] == c2]
            dlfv_df1 = df1[[str(x) for x in range(1, 513)]]
            dlfv_df2 = df2[[str(x) for x in range(1, 513)]]

            r_coeff = pearsonr(
                np.mean(dlfv_df1), np.mean(dlfv_df2)
            )

            df_corr[c1][c2] = r_coeff[0]
            df_corr[c2][c1] = r_coeff[0]

        for c in colors:
            df_corr[c][c] = 1

        plt.close('all')
        sns.clustermap(df_corr, annot=True, cmap="Blues")  # , method='ward')
        # plt.show()
        plt.savefig(os.path.join(dir, f'{slide_name}_{kval}_corr_clustermap.jpg'), dpi=300)


# pearson coeffcient clustermap of color groups within all the csvs in the folder
# (multi slide hence there will be 2 colortracks: left will be slide and right will be the cluster)
# takes in directory with a dump of all the k<k_val> csv's
def create_correlation_clustermap_multi_slide(dir, kval='*'):
    # choose color to represent ach slide
    color_gen = unique_colors.next_color_generator(scaled=True, mode='rgb')
    group_to_color_rgb = {}
    group_to_color_rgb_name = {}
    for fp in glob.glob(os.path.join(dir, f'*_k{kval}.csv')):
        color_ = next(color_gen)
        group_to_color_rgb[pathlib.Path(fp).stem] = color_['val']
        group_to_color_rgb_name[pathlib.Path(fp).stem] = color_['name']

    df_mapping = OrderedDict()
    df_mapping_english_keys = []
    for fp in glob.glob(os.path.join(dir, f'*_k{kval}.csv')):
        df = pd.read_csv(fp)
        for color, rows in df.groupby('Cluster_color_name'):
            df_mapping[
                (group_to_color_rgb[pathlib.Path(fp).stem], unique_colors.SCALED_RGB_COLORS[color])
            ] = rows[[str(x) for x in range(1, 512 + 1)]].mean().values
            # the above mapping has keys as rgb values to work directly with the colortrack. this is human readable
            # version. ie so we can use in df_corr labels to get extracted ordering
            df_mapping_english_keys.append((pathlib.Path(fp).stem, color))

    df_corr = pd.DataFrame(np.zeros((len(df_mapping), len(df_mapping))))
    df_corr.columns = df_mapping.keys()
    df_corr.index = df_mapping.keys()

    for color, dlfv in df_mapping.items():
        for color_comp, dlfv_comp in df_mapping.items():
            if color != color_comp:
                r_coeff = pearsonr(dlfv, dlfv_comp)

                df_corr[color][color_comp] = r_coeff[0]
                df_corr[color_comp][color] = r_coeff[0]

    for c in df_mapping.keys():
        df_corr[c][c] = 1

    # change to human readable labels. same order as df_mapping.keys() due to ordereddict
    df_corr.columns = df_mapping_english_keys
    df_corr.index = df_mapping_english_keys

    # NOTE: REQUIRED! sets up the required format
    colors = pd.DataFrame(df_mapping.keys())
    colors = [colors[i] for i in colors.columns]

    g = sns.clustermap(df_corr.values, cmap="Blues", row_colors=colors)

    # plt.show()
    plt.savefig(os.path.join(dir, f'multi_slide_corr_clustermap.jpg'), dpi=300)

    g.data2d.to_csv(os.path.join(dir, f'r_values_df.csv'), index=False)

    import json
    with open(os.path.join(dir, 'colortrack_mapping_SLIDE.json'), 'w') as f:
        json.dump(group_to_color_rgb_name, f, indent=4)

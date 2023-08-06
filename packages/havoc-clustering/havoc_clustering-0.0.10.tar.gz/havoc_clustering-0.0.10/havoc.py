import glob
import os
import cv2
import ast
import pathlib
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import MinMaxScaler
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from tensorflow.keras.backend import clear_session
import matplotlib as mpl
from scipy.cluster.hierarchy import dendrogram, linkage
import pandas as pd

from general_utility.ai.tileextractor import TileExtractor
from general_utility.image_creator import ImageCreator
from general_utility.slide import Slide
from general_utility import unique_colors
import correlation_of_dlfv_groups


class HAVOC:

    def __init__(self, slide, feature_extractor_path, out_dir, tile_size=512, hd_backdrop=False):

        self.feature_extractor_path = feature_extractor_path

        self.slide = slide
        self.out_dir = os.path.join(out_dir, slide.name)
        pathlib.Path(self.out_dir).mkdir(parents=True, exist_ok=True)
        self.tile_size = tile_size

        # scale trimmed dimensions according to how we scaled our tile size
        te = TileExtractor(slide, tile_size)
        r = te.tile_size_resize_factor

        image_creator = ImageCreator(
            height=te.trimmed_height / r,
            width=te.trimmed_width / r,
            scale_factor=16,  # make resulting image size smaller
            channels=te.chn
        )

        if hd_backdrop:
            self._initialize()
        else:
            # Initialize using the slide's thumbnail
            thumbnail_factor = 25
            thumbnail = slide.get_thumbnail(thumbnail_factor)
            thumbnail = cv2.cvtColor(np.array(thumbnail), cv2.COLOR_RGB2BGR)
            thumbnail = thumbnail[:(te.trimmed_height // thumbnail_factor), :(te.trimmed_width // thumbnail_factor),
                        ...]
            image_creator.image = cv2.resize(thumbnail, image_creator.image.shape[:2][::-1])

        self.image_creator = image_creator

    def run(self, k_vals=[9], min_non_blank_amt=0.5, layer_name='global_average_pooling2d_1', save_tiles=False):
        self.process_dlfvs(min_non_blank_amt, layer_name)
        self.make_colortile(save_tiles, k_vals)
        correlation_of_dlfv_groups.create_correlation_clustermap_single_slide(self.out_dir)

    def process_dlfvs(self, min_non_blank_amt, layer_name):
        te = TileExtractor(self.slide, self.tile_size)
        gen = te.iterate_tiles2(min_non_blank_amt=min_non_blank_amt, batch_size=4)

        from tensorflow.keras.models import load_model
        from general_utility.ai.model_utils import ModelUtils

        coors = []
        dlfvs = []
        feat_extractor_model = load_model(self.feature_extractor_path)
        for res in gen:
            tiles, currcoors = res['tiles'], res['coordinates']
            batch = ModelUtils.prepare_images(tiles)
            currdlfvs = np.concatenate(
                ModelUtils.get_layer_datas(feat_extractor_model, batch, layers=[layer_name]))
            coors.append(currcoors)
            dlfvs.append(currdlfvs)

        self.coors = np.concatenate(coors)
        self.dlfvs = np.concatenate(dlfvs)

        clear_session()

    def make_colortile(self, save_tiles, k_vals):
        scaled_convolved_data = MinMaxScaler(copy=False).fit_transform(self.dlfvs)

        # iterating over cluster values
        for k in k_vals:

            if k > len(self.dlfvs): break

            cluster_info_df = self.create_cluster_info_df(
                X=scaled_convolved_data,
                data_labels=[str(x) for x in self.coors.tolist()],
                k=k,
                linkage_method='ward'
            )
            cluster_info_df['Coor'] = cluster_info_df['DL'].apply(lambda x: ast.literal_eval(x))

            self.make_dendrogram(cluster_info_df)
            self.make_tsne(cluster_info_df)

            # NOTE: saving the entire file can be large...only do when needed
            cluster_info_df.to_csv(os.path.join(self.out_dir, '{}_k{}.csv'.format(self.slide.name, k)), index=False)

            self.create_colortiled_slide(cluster_info_df, save_tiles=save_tiles)

    '''
    Use this when we want to make "good copies". Initialize using thumbnail instead during development/testing 
    '''

    def _initialize(self):
        '''
        This is the time consuming step. Adding the actual colors is fast
        '''

        print('Initializing image creator...please be patient')

        te = TileExtractor(self.slide, self.tile_size)

        # first add the tiles to the blank image
        for res in te.iterate_tiles2(batch_size=1):
            tile, coor = res['tiles'][0], res['coordinates'][0]
            self.image_creator.add_tile(tile, coor)

        print('DONE')

    # cluster the data into k groups and assign each a color
    def create_cluster_info_df(self, X, data_labels, k=7, linkage_method='complete'):

        cluster = AgglomerativeClustering(n_clusters=k, linkage=linkage_method)
        cluster_labels = cluster.fit_predict(X)

        temp_df = pd.DataFrame({'Cluster': cluster_labels, 'DL': data_labels})

        color_gen = unique_colors.next_color_generator(scaled=False, mode='rgb', shuffle=False)
        cluster_to_color = {c: next(color_gen) for c in sorted(np.unique(cluster_labels))}
        temp_df['Cluster_color_name'] = temp_df['Cluster'].apply(lambda x: cluster_to_color[x]['name'])
        temp_df['Cluster_color_rgb'] = temp_df['Cluster'].apply(lambda x: cluster_to_color[x]['val'])
        temp_df[list(range(1, 512 + 1))] = X
        # sort by color
        temp_df = temp_df.sort_values('Cluster_color_name')

        return temp_df

    def create_colortiled_slide(self, cluster_info_df, save_tiles=False, copy=False):

        # make the color folders for saving the actual tiles
        if save_tiles:
            for c in cluster_info_df['Cluster_color_name'].unique():
                pathlib.Path(os.path.join(self.out_dir, c)).mkdir(parents=True, exist_ok=True)

            for res in TileExtractor(self.slide, self.tile_size).iterate_tiles2(batch_size=1):
                tile, coor = res['tiles'][0], res['coordinates'][0]

                # save in color folder
                # NOTE: this if statement is only for the case where we basically not using all tiles (ie blank)
                res = cluster_info_df[cluster_info_df['Coor'].apply(lambda x: all(x == coor))]
                if len(res):
                    # get the cluster this coordinate belongs to and then the color that cluster belongs to
                    curr_color = res['Cluster_color_name'].values[0]
                    curr_sp = os.path.join(self.out_dir, curr_color, str(tuple(coor)) + '.jpg')
                    cv2.imwrite(curr_sp, tile)

        # this allows us to re-use the initialized image with various desired borders
        if copy:
            img_copy = self.image_creator.image.copy()

        # group on cluster color and get all the associated coordinates
        for color, coors in cluster_info_df.groupby('Cluster_color_rgb')['Coor'].apply(list).to_dict().items():
            # change rgb to bgr
            self.image_creator.add_borders(coors, color=color[::-1], add_big_text=False)

        cv2.imwrite(
            os.path.join(self.out_dir, '{}_k{}_colortiled.jpg'.format(self.slide.name,
                                                                      cluster_info_df['Cluster_color_name'].nunique())),
            self.image_creator.image
        )

        if copy:
            self.image_creator.image = img_copy

    def make_tsne(self, cluster_info_df):
        import matplotlib as mpl
        print('Generating TSNE')

        scaled_fv_data = MinMaxScaler(copy=False).fit_transform(cluster_info_df[list(range(1, 512 + 1))])
        res = TSNE(2).fit_transform(scaled_fv_data)

        cluster_info_df['TSNE_X'] = res[:, 0]
        cluster_info_df['TSNE_Y'] = res[:, 1]

        cluster_info_df['Cluster_color_hex'] = cluster_info_df['Cluster_color_rgb'].apply(
            lambda rgb_tuple: mpl.colors.rgb2hex([x / 255. for x in rgb_tuple]))

        # go through each cluster and get the data belonging to it. plot it with its corresponding color
        plt.close('all')
        for hex, rows in cluster_info_df.groupby('Cluster_color_hex'):
            plt.scatter(
                rows['TSNE_X'],
                rows['TSNE_Y'],
                s=20,
                c=[hex] * len(rows)
            )

        sp = os.path.join(self.out_dir,
                          '{}_k{}_tsne.jpg'.format(self.slide.name, cluster_info_df['Cluster'].nunique()))
        plt.savefig(sp, dpi=200, bbox_inches='tight')

    def make_dendrogram(self, cluster_info_df):
        cluster_info_df = cluster_info_df.reset_index(drop=True)

        cluster_info_df['Cluster_color_hex'] = cluster_info_df['Cluster_color_rgb'].apply(
            lambda rgb_tuple: mpl.colors.rgb2hex([x / 255. for x in rgb_tuple]))
        Z = linkage(cluster_info_df[list(range(1, 512 + 1))], 'ward')

        # NOTE: THIS IS FOR MAKING DENDROGRAM COLORS MATCH THE COLORTILE SLIDE
        link_cols = {}
        for i, i12 in enumerate(Z[:, :2].astype(int)):
            c1, c2 = (link_cols[x] if x > len(Z) else cluster_info_df.loc[x]['Cluster_color_hex']
                      for x in i12)
            link_cols[i + 1 + len(Z)] = c1 if c1 == c2 else '#0000FF'

        plt.close('all')
        plt.title('Hierarchical Clustering Dendrogram')
        plt.ylabel('distance')

        dendrogram(
            Z,
            no_labels=True,
            color_threshold=None,
            link_color_func=lambda x: link_cols[x]
        )

        sp = os.path.join(self.out_dir,
                          '{}_k{}_dendrogram.jpg'.format(self.slide.name, cluster_info_df['Cluster'].nunique()))
        plt.savefig(sp, dpi=200, bbox_inches='tight')

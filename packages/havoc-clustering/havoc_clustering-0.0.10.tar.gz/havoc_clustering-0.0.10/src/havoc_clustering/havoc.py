import os
import shutil
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
from tensorflow.keras.models import load_model

from havoc_clustering.general_utility.ai.tileextractor import TileExtractor
from havoc_clustering.general_utility.image_creator import ImageCreator
from havoc_clustering import correlation_of_dlfv_groups
from havoc_clustering.general_utility.ai.model_utils import ModelUtils
from havoc_clustering.general_utility import unique_colors


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

    def run(self, k_vals=[9], min_non_blank_amt=0.5, layer_name='global_average_pooling2d_1', **kwargs):

        save_tiles_k_vals = kwargs['save_tiles_k_vals'] if 'save_tiles_k_vals' in kwargs else ()
        make_tsne = kwargs.get('make_tsne', True)
        make_dendrogram = kwargs.get('make_dendrogram', True)
        make_corr_map = kwargs.get('make_corr_map', True)

        # we save all the tiles to a tmp folder and then copy the tiles into color folders when we do colortiling
        if not set(save_tiles_k_vals).issubset(k_vals):
            raise Exception('save_tiles_k_vals must be a subset of k_vals')

        df = self.process_dlfvs(min_non_blank_amt, layer_name, len(save_tiles_k_vals))
        df['Coor'] = df['Coor'].apply(ast.literal_eval)

        for k in k_vals:
            cluster_info_df = self.create_cluster_info_df(
                df[[str(x) for x in range(1, 512 + 1)]], k, linkage_method='ward')
            df = pd.concat([cluster_info_df, df], axis=1)

        df.to_csv(os.path.join(self.out_dir, f'{self.slide.name}_cluster_info_df.csv'), index=None)

        for k in k_vals:
            if make_dendrogram:
                self.make_dendrogram(df, target_k=k)
            if make_tsne:
                self.make_tsne(df, target_k=k)
            if make_corr_map:
                correlation_of_dlfv_groups.create_correlation_clustermap_single_slide(self.out_dir, target_k=k)

            self.create_colortiled_slide(df, target_k=k, save_tiles=k in save_tiles_k_vals)

        if len(save_tiles_k_vals):
            # done copying to k color folders
            shutil.rmtree(os.path.join(self.out_dir, 'tiles', 'tmp'))

    def process_dlfvs(self, min_non_blank_amt, layer_name, save_tiles):
        te = TileExtractor(self.slide, self.tile_size)
        gen = te.iterate_tiles2(min_non_blank_amt=min_non_blank_amt, batch_size=4)

        if save_tiles:
            # we save all the tiles to a tmp folder and then copy the tiles into color folders when we do colortiling
            pathlib.Path(os.path.join(self.out_dir, 'tiles', 'tmp')).mkdir(parents=True, exist_ok=True)

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

            if save_tiles:
                # each iteration contains a batch of tiles
                for pos in range(len(tiles)):
                    curr_sp = os.path.join(self.out_dir, 'tiles', 'tmp', str(tuple(currcoors[pos])) + '.jpg')
                    cv2.imwrite(curr_sp, tiles[pos])

        dlfvs = np.concatenate(dlfvs)
        coors = np.concatenate(coors)

        scaled_dlfvs = MinMaxScaler(copy=False).fit_transform(dlfvs)

        df = pd.DataFrame(scaled_dlfvs, columns=[str(x) for x in range(1, 512 + 1)])
        df['Slide'] = [self.slide.name] * len(df)
        df['Coor'] = [str(x) for x in coors.tolist()]

        clear_session()

        return df

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
    def create_cluster_info_df(self, X, k, linkage_method='complete'):

        cluster = AgglomerativeClustering(n_clusters=k, linkage=linkage_method)
        cluster_labels = cluster.fit_predict(X)

        temp_df = pd.DataFrame({f'Cluster_{k}': cluster_labels})

        color_gen = unique_colors.next_color_generator(scaled=False, mode='rgb', shuffle=False)
        cluster_to_color = {c: next(color_gen) for c in sorted(np.unique(cluster_labels))}
        temp_df[f'Cluster_color_name_{k}'] = temp_df[f'Cluster_{k}'].apply(lambda x: cluster_to_color[x]['name'])
        temp_df[f'Cluster_color_rgb_{k}'] = temp_df[f'Cluster_{k}'].apply(lambda x: cluster_to_color[x]['val'])

        return temp_df

    def create_colortiled_slide(self, cluster_info_df, target_k, save_tiles=False, copy=False):

        # make the color folders for saving the actual tiles
        if save_tiles:
            for c in cluster_info_df[f'Cluster_color_name_{target_k}'].unique():
                pathlib.Path(os.path.join(self.out_dir, 'tiles', str(target_k), c)).mkdir(parents=True, exist_ok=True)

                coords = cluster_info_df['Coor'][cluster_info_df[f'Cluster_color_name_{target_k}'] == c]
                for _, coord in coords.items():
                    fname = str(tuple(coord)) + '.jpg'
                    try:
                        shutil.copy2(os.path.join(self.out_dir, 'tiles', 'tmp', fname),
                                     os.path.join(self.out_dir, 'tiles', str(target_k), c, fname))
                    except FileNotFoundError:
                        print(f'Tile for coordinate {coord} not found')

        # this allows us to re-use the initialized image with various desired borders
        if copy:
            img_copy = self.image_creator.image.copy()

        # group on cluster color and get all the associated coordinates
        for color, coors in cluster_info_df.groupby(f'Cluster_color_rgb_{target_k}')['Coor'].apply(
                list).to_dict().items():
            # change rgb to bgr
            self.image_creator.add_borders(coors, color=color[::-1], add_big_text=False)

        cv2.imwrite(
            os.path.join(self.out_dir, '{}_k{}_colortiled.jpg'.format(self.slide.name, target_k)),
            self.image_creator.image
        )

        if copy:
            self.image_creator.image = img_copy

    def make_tsne(self, cluster_info_df, target_k):
        print('Generating TSNE')

        res = TSNE(2).fit_transform(cluster_info_df[[str(x) for x in range(1, 512 + 1)]])

        tsne_df = pd.DataFrame({'TSNE_X': res[:, 0], 'TSNE_Y': res[:, 1]})

        tsne_df['Cluster_color_hex'] = cluster_info_df[f'Cluster_color_rgb_{target_k}'].apply(
            lambda rgb_tuple: mpl.colors.rgb2hex([x / 255. for x in rgb_tuple]))

        # go through each cluster and get the data belonging to it. plot it with its corresponding color
        plt.close('all')
        for hex, rows in tsne_df.groupby('Cluster_color_hex'):
            plt.scatter(
                rows['TSNE_X'],
                rows['TSNE_Y'],
                s=20,
                c=[hex] * len(rows)
            )

        sp = os.path.join(self.out_dir, '{}_k{}_tsne.jpg'.format(self.slide.name, target_k))
        plt.savefig(sp, dpi=200, bbox_inches='tight')

    def make_dendrogram(self, cluster_info_df, target_k):

        cluster_color_hex = cluster_info_df[f'Cluster_color_rgb_{target_k}'].apply(
            lambda rgb_tuple: mpl.colors.rgb2hex([x / 255. for x in rgb_tuple]))
        Z = linkage(cluster_info_df[[str(x) for x in range(1, 512 + 1)]], 'ward')

        # NOTE: THIS IS FOR MAKING DENDROGRAM COLORS MATCH THE COLORTILE SLIDE
        link_cols = {}
        for i, i12 in enumerate(Z[:, :2].astype(int)):
            c1, c2 = (link_cols[x] if x > len(Z) else cluster_color_hex.loc[x]
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

        sp = os.path.join(self.out_dir, '{}_k{}_dendrogram.jpg'.format(self.slide.name, target_k))
        plt.savefig(sp, dpi=500, bbox_inches='tight')

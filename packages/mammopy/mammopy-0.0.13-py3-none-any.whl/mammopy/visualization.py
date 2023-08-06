import sys, os
sys.path.insert(0, os.path.abspath('.'))
import numpy as np
import matplotlib.pyplot as plt
import mammopy as mi


class visualization():


    def visualize_breast_dense_segmentation(image, breast_prediction_mask, dense_prediction_mask):
        edges = mi.analysis.canny_edges(breast_prediction_mask)
        #plotttig the results
        combined_sigm, axes = plt.subplots(1,2, figsize = (15,10),squeeze=False)
        axes[0, 0].set_title('Image', fontsize=16)
        axes[0, 1].set_title("Breast and dense tissue segmentation", fontsize=20)
        axes[0, 0].imshow(image, cmap='gray')
        axes[0, 0].set_axis_off()
        axes[0, 1].imshow(image, cmap='gray')
        axes[0, 1].imshow(mi.analysis.mask_to_rgba(edges, color='red'), cmap='gray')
        axes[0, 1].imshow(mi.analysis.mask_to_rgba(dense_prediction_mask, color='green'), cmap='gray', alpha=0.7)
        axes[0, 1].set_axis_off()

        brest_sigm, axes = plt.subplots(1,1, squeeze=False)
        axes[0, 0].imshow(image, cmap='gray')
        axes[0, 0].imshow(mi.analysis.mask_to_rgba(edges, color='red'), cmap='gray')
        axes[0, 0].set_axis_off()

        dens_sigm, axes = plt.subplots(1,1, squeeze=False)
        axes[0, 0].imshow(image, cmap='gray')
        axes[0, 0].imshow(mi.analysis.mask_to_rgba(dense_prediction_mask, color='green'), cmap='gray', alpha=0.7)
        axes[0, 0].set_axis_off()        

        return combined_sigm, brest_sigm, dens_sigm

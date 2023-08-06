# MedSimilarity

[![DOI](https://zenodo.org/badge/583443319.svg)](https://zenodo.org/badge/latestdoi/583443319)

## What is MedSimilarity?

MedSimilarity is an open source Python to compare 2D medical images.

### Citation

If you use this software, please cite it in your publication using:

```text
@software{medsimilarity,
  title={MedSimilarity},
  author={Kulkarni, Pranav},
  month={May},
  year={2023},
  url={https://github.com/UM2ii/MedSimilarity},
  doi={10.5281/zenodo.7937894}
}
```

## Getting Started

MedSimilarity is currently not available through `pip`, but you can manually install it.

### Manual Installation

You can manually install MedSimilarity as follows:

```bash
$ git clone https://github.com/UM2ii/MedSimilarity
$ pip install MedSimilarity/
```

### Example Notebook

We have provided an example notebook in this repository, along with 100 test images to experiment with. You can find the example notebook [here](./notebooks/example.ipynb).

## Documentation

### `medsimilarity.structural_similarity`

Computes the mean structural similarity index measure (SSIM) between two images. This implementation is an extension of `skimage.metrics.structural_similarity` (https://scikit-image.org/docs/stable/api/skimage.metrics.html#skimage.metrics.structural_similarity) with preprocessing steps for medical images.

#### Arguments:
img1, img2: PIL.Image
  Input images

#### Returns:
score: float
  The mean structural similarity index measure over the image
grad: ndarray
  The gradient of the structural similarity between img1 and img2
diff: ndarray
  The full SSIM image

#### Notes:
- Structural similarity is not invariant to transformations

### `medsimilarity.structural_comparison`

Computes the pairwise structural similarity index measure (SSIM) between an image and a dataset and returns the top K matches.  

#### Arguments:
img: str
  Path to image
dataset: list
  List containing paths to each image in dataset
top_k: int, optional
  Number of best matches for `img` in `dataset`
use_multiprocessing: bool, optional
  Enables spawning of multiple processes to speed up pairwise SSIM calculation

#### Returns:
score: ndarray
  The `top_k` matches for `img` in `dataset` with SSIM score

### `medsimilarity.dense_vector_comparison`

Computes the cosine similarity scores using dense vector representations (DVRS) between an image and dataset and returns the top K matches. This method uses [SentenceTransformers](https://www.sbert.net/) ViT-B transformer for computation.

#### Arguments:
img: str
  Path to image
dataset: list
  List containing paths to each image in dataset
top_k: int, optional
  Number of best matches for `img` in `dataset`
use_multiprocessing: bool, optional
  Enables encoding images into embeddings using multiprocessing. If `device` is 'cuda', images are encoded using multiple GPUs. If `device` is 'cpu', multiple CPUs are used
device: str, optional
  Specifies device to move all resources to. Use 'cuda' to enable GPU acceleration. If left blank, by default 'cuda' is used if available. If not, 'cpu' is used

#### Returns:
score: ndarray
  The `top_k` matches for `img` in `dataset` with DVRS score

### `medsimilarity.combined_score`

#### Experimental!
Computes the combined score from structural similarity index measure (SSIM) and dense vector representations (DVRS) scores for a pair of images using the formula:

```text
x_combined = sqrt(x_ssim)*(x_dvrs)^2
```

#### Arguments:
x_ssim: float
  The SSIM score for pair of images
x_dvrs: float
  The DVRS score for pair of images

#### Returns:
x_combined: float
  Combined score for pair of images

#### Notes:
- This worked well in my testing but please take this with a grain of salt!
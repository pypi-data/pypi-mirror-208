"""
MedSimilarity 
"""

from PIL import Image
import numpy as np
import skimage.metrics
import multiprocessing
from functools import partial
from tqdm.contrib.concurrent import process_map
from sentence_transformers import SentenceTransformer, util
import torch
from . import utils

def structural_similarity(img1, img2):
  """
  Computes the mean structural similarity index measure (SSIM) between two images. This implementation is an extension of `skimage.metrics.structural_similarity` (https://scikit-image.org/docs/stable/api/skimage.metrics.html#skimage.metrics.structural_similarity) with preprocessing steps for medical images.

  ## Arguments:
  img1, img2: PIL.Image
    Input images

  ## Returns:
  score: float
    The mean structural similarity index measure over the image
  grad: ndarray
    The gradient of the structural similarity between img1 and img2
  diff: ndarray
    The full SSIM image

  ## Notes:
  - Structural similarity is not invariant to transformations
  """
  # Ensure both images are grayscale
  if img1.mode != 'L' or img2.mode != 'L':
    img1 = img1.convert('L')
    img2 = img2.convert('L')
  # Resize to match dimensions
  if img1.size != img2.size:
    if img1.size > img2.size:
      img1 = img1.resize(img2.size)
    else:
      img2 = img2.resize(img1.size)
  # Calculate SSIM
  score, grad, diff = skimage.metrics.structural_similarity(
    np.array(img1), 
    np.array(img2), 
    full = True,
    gradient = True
  )
  return score, grad, diff

def __structural_comparison_worker(img1, img2):
  """
  Multiprocessing worker for pairwise structural similarity index measure (SSIM) between an image and a dataset.

  ## Arguments:
  img1, img2: str
    Path to pair of images

  ## Returns:
  score: ndarray
    Pairwise SSIM score between `img1` and `img2`
  """
  score, _, _ = structural_similarity(Image.open(img1), Image.open(img2))
  return [utils.get_filename(img1), score]

def structural_comparison(
  img, 
  dataset, 
  top_k = 50, 
  use_multiprocessing = True
):
  """
  Computes the pairwise structural similarity index measure (SSIM) between an image and a dataset and returns the top K matches.  

  ## Arguments:
  img: str
    Path to image
  dataset: list
    List containing paths to each image in dataset
  top_k: int, optional
    Number of best matches for `img` in `dataset`
  use_multiprocessing: bool, optional
    Enables spawning of multiple processes to speed up pairwise SSIM calculation

  ## Returns:
  score: ndarray
    The `top_k` matches for `img` in `dataset` with SSIM score
  """
  if use_multiprocessing:
    max_workers = multiprocessing.cpu_count()
    matches = process_map(partial(__structural_comparison_worker, img2=img), dataset, max_workers=max_workers, chunksize=1)
  else:
    matches = []
    for i in dataset:
      score, _, _ = structural_similarity(Image.open(i), Image.open(img))
      matches += [[utils.get_filename(i), score]]
  matches = np.array(matches, dtype=object)
  return matches[np.argsort(matches[:, 1])][::-1][:top_k]

def dense_vector_comparison(
  img, 
  dataset, 
  top_k = 50, 
  use_multiprocessing = True, 
  device = None
):
  """
  Computes the cosine similarity scores using dense vector representations (DVRS) between an image and dataset and returns the top K matches. This method uses [SentenceTransformers](https://www.sbert.net/) ViT-B transformer for computation.

  ## Arguments:
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

  ## Returns:
  score: ndarray
    The `top_k` matches for `img` in `dataset` with DVRS score
  """
  if device == None:
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
  # This method is invariant to transformations
  model = SentenceTransformer('clip-ViT-B-32', device=device)
  # Lazyload images
  sentences = [Image.open(img)] + [Image.open(path) for path in dataset]
  if use_multiprocessing:
    embds = model.encode_multi_process(
      sentences, 
      model.start_multi_process_pool()
    )
  else:
    embds = model.encode(sentences)
  scores = util.paraphrase_mining_embeddings(
    embds, 
    top_k = top_k
  )
  scores = np.array(scores, dtype=object)
  scores = (scores[np.where(scores[:,1] == 0)[0]])[:,[2,0]]
  matches = []
  for idx, score in scores:
    matches += [[utils.get_filename(dataset[int(idx)-1]), score]]
  return np.array(matches, dtype=object)

'''Combine scores from both methods'''
def combined_score(x_ssim, x_dvrs):
  """
  ### Experimental!
  Computes the combined score from structural similarity index measure (SSIM) and dense vector representations (DVRS) scores for a pair of images using the formula:

  ```text
  x_combined = sqrt(x_ssim)*(x_dvrs)^2
  ```

  ## Arguments:
  x_ssim: float
    The SSIM score for pair of images
  x_dvrs: float
    The DVRS score for pair of images

  ## Returns:
  x_combined: float
    Combined score for pair of images

  ## Notes:
  - This worked well in my testing but please take this with a grain of salt!
  """
  return np.sqrt(x_ssim)*np.power(x_dvrs, 2)
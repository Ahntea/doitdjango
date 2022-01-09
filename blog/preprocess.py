import torch
from skimage import io, transform
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
import pandas as pd
import numpy as np
import os
from PIL import Image
import face_recognition

class CustomDataset(torch.utils.data.Dataset): 
  def __init__(self, file_url, root_dir, transform=None):
    self.file_url = file_url
    self.root_dir = root_dir
    self.transform = transform
  
  def get_face(self, image_name):
    ## 얼굴 윤곽 추출
    image = face_recognition.load_image_file(image_name)
    face_locations = face_recognition.face_locations(image)
    # face_location = face_recognition.face_locations(image_name)
    if len(face_locations) != 1:
      return io.imread(image_name)
    else:
      for face_location in face_locations:
        top, right, bottom, left = face_location
        # You can access the actual face itself like this:
        face_image = image[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)
        # io.imshow(np.asarray(pil_image))
        return np.asarray(pil_image)

  def __getitem__(self, idx): 
    image_name = os.path.join(self.root_dir, self.file_url)
    image = self.get_face(image_name)

    # image = io.imread(image_name)
    label = 35

    # sample = {'image' : image, 'label' : label}
    sample = {'image' : image, 'label' : np.array(label)}
    if self.transform:
      sample = self.transform(sample)
    return sample


class Rescale(object):

    def __init__(self, output_size):
        assert isinstance(output_size, (int, tuple))
        self.output_size = output_size

    def __call__(self, sample):
        image, label = sample['image'], sample['label']
        # image, age =sample
        h, w = image.shape[:2]
        if isinstance(self.output_size, int):
            if h > w:
                new_h, new_w = self.output_size * h / w, self.output_size
            else:
                new_h, new_w = self.output_size, self.output_size * w / h
        else:
            new_h, new_w = self.output_size

        new_h, new_w = int(new_h), int(new_w)

        img = transform.resize(image, (new_h, new_w))


        return {'image' : img, 'label' : label}
    
class ToTensor(object):
    """Convert ndarrays in sample to Tensors."""

    def __call__(self, sample):
        image = sample['image']
        label = sample['label']

        img = image.transpose((2, 0, 1))

        return torch.from_numpy(img).float(), torch.from_numpy(label).float()
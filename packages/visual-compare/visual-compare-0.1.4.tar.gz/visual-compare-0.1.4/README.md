Visual Compare
==============

## Installation

```commandline
pip install visual-compare
```

## Examples

### Compare images ###

```python
from visual_compare.doc.visual_test import VisualTest

def get_path(filename):
    image_base = '../../files/images/'
    return image_base + filename

reference_image = get_path('123.png')
test_image = get_path('124.png')
vt = VisualTest()
res = vt.compare_images(reference_image, test_image)
print(res)
assert vt.is_different is True
```

 Result as follows

![1.jpg](https://github.com/cuidingyong/visual-compare/raw/main/files/result/1.jpg)

### Compare images with mask ###

```python
from visual_compare.doc.visual_test import VisualTest

def get_path(filename):
    image_base = '../../files/images/'
    return image_base + filename

reference_image = get_path('123.png')
test_image = get_path('124.png')
mask_images = [get_path('000.png')]
vt = VisualTest()
mask = vt.generate_mask(reference_image, mask_images)
res = vt.compare_images(reference_image, test_image, mask=mask)
print(res)
assert vt.is_different is True
```

 Result as follows

![2.jpg](https://github.com/cuidingyong/visual-compare/raw/main/files/result/2.jpg)
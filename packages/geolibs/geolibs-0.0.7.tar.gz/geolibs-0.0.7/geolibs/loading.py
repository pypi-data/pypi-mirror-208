import warnings 
import os.path as osp
from typing import Optional, List
import io 

import tarfile
import numpy as np
import cv2 

import mmengine.fileio as fileio
from mmengine.registry import TRANSFORMS
from mmcv.transforms import LoadImageFromFile
from mmcv.transforms import LoadAnnotations as MMCV_LoadAnnotations

from rasterio.io import MemoryFile 


def bandsfrombytes(content: bytes,
                band_ids: Optional[List[int]] = None) -> dict:
    """Read multiple bands from bytes.
    Args:
        content (bytes): raster bytes got from files or other streams.
        band_ids (list of int): band ids to be selected
    Returns:
        dict: Loaded bands as dict map with band keys and band array.
    Examples:
        >>> tif_path = '/path/to/img.tif'
        >>> with open(tif_path, 'rb') as f:
        >>>     tif_buff = f.read()
        >>> bands = mmcv.bandsfrombytes(tif_buff, band_ids=[0, 1, 2])
    """
    with MemoryFile(content) as memfile:
        r = memfile.open()
        bands = r.read()
        metadata = r.profile
        r.close()
        
        if not band_ids:
            return bands, metadata
        else:
            return bands[band_ids], metadata


def bandsfromtarbytes(content: bytes,
                band_substrings: List[str]) -> dict:
    """Read bands from tar bytes.
    Args:
        content (bytes): raster or tar bytes got from files or other streams.
        band_substrings (list of str): bands substring present in file names inside tar
    Returns:
        dict: Loaded bands as dict map with band keys and band array.
    Examples:
        >>> tar_path = '/path/to/img.tar'
        >>> with optn(tar_path, 'rb') as f:
        >>>     tar_buff = f.read()
        >>> img = mmcv.bandsfrombytes(tar_buff, band_substrings=['B01', 'B02', 'B03'])
    """
    with io.BytesIO(content) as buff:
        tar = tarfile.open(fileobj=buff, mode='r')
        bands = {}
        metadata = {}
        for member in tar.getmembers():
            if 'tif' in member.name:
                r = MemoryFile(tar.extractfile(member.name).read()).open()
                bands[member.name] = r.read()
                metadata[member.name] = r.profile
        
        out_bands = {}
        out_metadata = {}
        for band_str in band_substrings:
            for k in bands.keys():
                if band_str in k:
                    out_bands[band_str] = bands[k]
                    out_metadata[band_str] = metadata[k]

    return out_bands, out_metadata


@TRANSFORMS.register_module()
class LoadBandsFromFile(LoadImageFromFile):
    """Load bands from file.
    Required keys are "img_prefix" and "img_info" (a dict that must contain the
    key "filename"). Added or updated keys are "filename", "img", "img_shape",
    "ori_shape" (same as `img_shape`) and "img_norm_cfg" (means=0 and stds=1).
    "img_meta" key contains raster profile metadata.
    Args:
        to_float32 (bool): Whether to convert the loaded image to a float32
            numpy array. If set to False, the loaded image is an uint8 array.
            Defaults to False.
        band_ids (list(int)): List of bands to subsample from loaded band files.
            Defaults to all bands.
        file_client_args (dict): Arguments to instantiate a FileClient.
            See :class:`mmcv.fileio.FileClient` for details.
            Defaults to ``dict(backend='disk')``.
    """

    def __init__(self,
                 to_float32=False,
                 gray2rgb=False,
                 band_ids=None,
                 file_client_args=dict(backend='disk')):
        self.band_ids = band_ids
        self.to_float32 = to_float32
        self.file_client_args = file_client_args.copy()
        self.file_client = None
        self.gray2rgb = gray2rgb

    def transform(self, results: dict):
        filename = results['img_path']
        if self.file_client_args is not None:
            file_client = fileio.FileClient.infer_client(
                self.file_client_args, filename)
            band_bytes = file_client.get(filename)
        else:
            band_bytes = fileio.get(
                filename, backend_args=self.backend_args)
        
        bands, metadata = bandsfrombytes(band_bytes, band_ids=self.band_ids)
        if self.gray2rgb or bands.shape[0] == 1:
            # assert bands.shape[0] == 1, "gray2rgb is only for grayscale images"
            bands = np.asarray([bands[0], bands[0], bands[0]])
        bands = bands.transpose(1, 2, 0)

        bands = self._make_patch(bands, results)
        if self.to_float32:
            bands = bands.astype(np.float32)
                
        results["img"] = bands
        results["img_shape"] = bands.shape[:2]
        results["ori_shape"] = bands.shape[:2]
        results["img_meta"] = metadata

        num_channels = 1 if len(bands.shape) < 3 else bands.shape[2]

        results['img_norm_cfg'] = dict(
                mean=np.zeros(num_channels, dtype=np.float32),
                std=np.ones(num_channels, dtype=np.float32),
                to_rgb=False)

        return results


    def _make_patch(self, bands, img_info):
        slice_x = img_info["slice_x"]
        slice_y = img_info["slice_y"]
        slice_w = img_info["slice_w"]
        slice_h = img_info["slice_h"]
        return bands[slice_y:slice_y+slice_h, slice_x:slice_x+slice_w, :].copy()


@TRANSFORMS.register_module()
class LoadVariableSizedBandsFromFile(LoadImageFromFile):
    """Load variable sized bands from tar file.
    Required keys are "img_prefix" and "img_info" (a dict that must contain the
    key "filename"). Added or updated keys are "filename", "img", "img_shape",
    "ori_shape" (same as `img_shape`) and "img_norm_cfg" (means=0 and stds=1).
    "img_{BAND_ID}" contains raster profile for band with band id.
    Args:
        band_substrings (list(str)): Band substrings that must match band file names present in the tar file.
            Required argument.
        to_float32 (bool): Whether to convert the loaded image to a float32
            numpy array. If set to False, the loaded image is an uint8 array.
            Defaults to False.
        file_client_args (dict): Arguments to instantiate a FileClient.
            See :class:`mmcv.fileio.FileClient` for details.
            Defaults to ``dict(backend='disk')``.
    """

    def __init__(self,
                 band_substrings,
                 to_float32=False,
                 file_client_args=dict(backend='disk')):
        self.band_substrings = band_substrings
        self.to_float32 = to_float32
        self.file_client_args = file_client_args.copy()
        self.file_client = None

    def transform(self, results: dict):
        filename = results['img_path']
        if self.file_client is None:
            self.file_client = fileio.FileClient.infer_client(
                    self.file_client_args, filename)
            
        bands_bytes = self.file_client.get(filename)
        bands, metadata = bandsfromtarbytes(bands_bytes, band_substrings=self.band_substrings)
        band_shapes = {}
        if self.to_float32:
            for band_id in bands.keys():
                bands[band_id] = bands[band_id].astype(np.float32)
                band_shapes[band_id] = bands[band_id].shape 

        results['filename'] = filename
        results['ori_filename'] = results['img_info']['filename']
        for band_id in bands.keys():
            results[band_id] = bands[band_id]
            results[band_id + '-meta'] = metadata[band_id]
        results['band_shapes'] = band_shapes
        results['ori_shapes'] = band_shapes
        num_channels = len(self.band_substrings)
        results['bands_norm_cfg'] = dict(
            mean=np.zeros(num_channels, dtype=np.float32),
            std=np.ones(num_channels, dtype=np.float32),
            to_rgb=False)
        return results

    def __repr__(self):
        repr_str = (f'{self.__class__.__name__}('
                    f'to_float32={self.to_float32}, '
                    f"band_substrings='{self.band_substrings}', "
                    f'file_client_args={self.file_client_args})')
        return repr_str

@TRANSFORMS.register_module()
class LoadMasks(MMCV_LoadAnnotations):
    """Load annotations for semantic segmentation provided by GeoEngine dataset.

    The annotation format is as the following:

    .. code-block:: python

        {
            # Filename of semantic segmentation ground truth file.
            'seg_map_path': 'a/b/c'
        }

    After this module, the annotation has been changed to the format below:

    .. code-block:: python

        {
            # in str
            'seg_fields': List
             # In uint8 type.
            'gt_seg_map': np.ndarray (H, W)
        }

    Required Keys:

    - seg_map_path (str): Path of semantic segmentation ground truth file.

    Added Keys:

    - seg_fields (List)
    - gt_seg_map (np.uint8)

    Args:
        reduce_zero_label (bool, optional): Whether reduce all label value
            by 1. Usually used for datasets where 0 is background label.
            Defaults to None.
        imdecode_backend (str): The image decoding backend type. The backend
            argument for :func:``mmcv.imfrombytes``.
            See :fun:``mmcv.imfrombytes`` for details.
            Defaults to 'pillow'.
        backend_args (dict): Arguments to instantiate a file backend.
            See https://mmengine.readthedocs.io/en/latest/api/fileio.htm
            for details. Defaults to None.
            Notes: mmcv>=2.0.0rc4, mmengine>=0.2.0 required.
    """

    def __init__(
        self,
        reduce_zero_label=None,
        backend_args=None,
        imdecode_backend='pillow',
    ) -> None:
        super().__init__(
            with_bbox=False,
            with_label=False,
            with_seg=True,
            with_keypoints=False,
            imdecode_backend=imdecode_backend,
            backend_args=backend_args)
        self.reduce_zero_label = reduce_zero_label
        if self.reduce_zero_label is not None:
            warnings.warn('`reduce_zero_label` will be deprecated, '
                          'if you would like to ignore the zero label, please '
                          'set `reduce_zero_label=True` when dataset '
                          'initialized')
        self.imdecode_backend = imdecode_backend

    def _load_seg_map(self, results: dict) -> None:
        """Private function to load semantic segmentation annotations.

        Args:
            results (dict): Result dict from :obj:``mmcv.BaseDataset``.

        Returns:
            dict: The dict contains loaded semantic segmentation annotations.
        """
        if self.reduce_zero_label is None:
            self.reduce_zero_label = results['reduce_zero_label']
        assert self.reduce_zero_label == results['reduce_zero_label'], \
            'Initialize dataset with `reduce_zero_label` as ' \
            f'{results["reduce_zero_label"]} but when load annotation ' \
            f'the `reduce_zero_label` is {self.reduce_zero_label}'
        h, w = results['slice_h'], results['slice_w']
        gt_semantic_seg = np.zeros((h, w), dtype=np.uint8)
        for annotation in results["instances"]:
            for poly in annotation['mask']:
                if len(poly):
                    pts = np.asarray(poly).reshape(-1, 1, 2).astype(np.int32)[:-1]
                    label = annotation['bbox_label'] + 1
                    gt_semantic_seg = cv2.fillPoly(gt_semantic_seg, pts=[pts], color=label)
        if self.reduce_zero_label:
            # avoid using underflow conversion
            gt_semantic_seg[gt_semantic_seg == 0] = 255
            gt_semantic_seg = gt_semantic_seg - 1
            gt_semantic_seg[gt_semantic_seg == 254] = 255

        results['gt_seg_map'] = gt_semantic_seg
        results['seg_fields'].append('gt_seg_map')

        return results

    def __repr__(self) -> str:
        repr_str = self.__class__.__name__
        repr_str += f'(reduce_zero_label={self.reduce_zero_label}, '
        repr_str += f"imdecode_backend='{self.imdecode_backend}', "
        repr_str += f'backend_args={self.backend_args})'
        return repr_str
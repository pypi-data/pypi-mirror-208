import json, copy
import numpy as np
from tqdm import tqdm

import pandas as pd 

from mmengine.registry import DATASETS
from torch.utils.data import Dataset
from typing import List, Union, Callable

from mmengine.dataset.base_dataset import Compose
from multiprocessing import Pool


@DATASETS.register_module()
class EngineCSV(Dataset):
    def __init__(self,
                 data_path: str,
                 raster_dir_path: str,
                 vector_dir_path: str,
                 split: str = "train",
                 class_title: str = None,
                 pipeline: List[Union[dict, Callable]] = [],
                 max_refetch: int = 1000):
        self.raster_data_path = f"{data_path}/{raster_dir_path}"
        self.vector_data_path = f"{data_path}/{vector_dir_path}"

        self.split = split
        self.class_title = class_title

        self.pipeline = Compose(pipeline)
        self.max_refetch = max_refetch

        self.get_data_list()
    
    def full_init(self):
        self.get_data_info

    def process_record(self, record):

        file_name = record["image:01"].split("/")[-1]
        file_path = f"{self.raster_data_path}/{file_name}"

        return {
            "img_path": file_path,
            "img_id": record["image-id"],
            "gt_label": self.class_map[record[self.class_title]]
        }

    def get_data_list(self):
        meta_path = f"{self.vector_data_path}/metadata.json"
        metadata = json.load(open(meta_path, "r"))

        if not self.class_title:
            self.CLASSES = metadata["label:metadata"][0]["options"]
            self.class_title = metadata["label:metadata"][0]["title"].replace(" ", "-").lower()
            self.class_title_idx = 0
        else:
            for idx, question in enumerate(metadata["label:metadata"]):
                if question["title"] == self.class_title:
                    self.CLASSES = question["options"]
                    self.class_title = self.class_title.replace(" ", "-").lower()
                    self.class_title_idx = idx 

        self._metainfo = {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "problemType": metadata["problemType"] if "problemType" in metadata else None,
            "question_title": metadata["label:metadata"][self.class_title_idx]["title"],
            "question_description": metadata["label:metadata"][self.class_title_idx]["description"],
            "classes": metadata["label:metadata"][self.class_title_idx]["options"]
        }

        self.class_map = {v:k for k,v in enumerate(metadata["label:metadata"][self.class_title_idx]["options"])}

        vec_path = f"{self.vector_data_path}/{metadata['dataset'][self.split]}"
        df = pd.read_csv(vec_path)
        records = df.to_dict('records')
        
        pool = Pool(16)
        self.data_list = list(tqdm(pool.imap(self.process_record, records), total=len(records)))
        pool.close()

    @property
    def metainfo(self) -> dict:
        """Get meta information of dataset.

        Returns:
            dict: meta information collected from ``BaseDataset.METAINFO``,
            annotation file and metainfo argument during instantiation.
        """
        return copy.deepcopy(self._metainfo)
    
    def get_data_info(self, idx: int):
        data = self.data_list[idx]
        data["sample_idx"] = idx

        return data
    
    def prepare_data(self, idx: int):
        data = self.get_data_info(idx)
        data['dataset'] = self
        return self.pipeline(data)

    def _rand_another(self):
        return np.random.randint(0, len(self))

    def __len__(self):
        return len(self.data_list)

    def __getitem__(self, idx: int):
        if self.split == "test":
            data = self.prepare_data(idx)
            if not data:
                raise Exception('Test time pipline should not get `None` data_sample')

        for _ in range(self.max_refetch+1):
            data = self.prepare_data(idx)
            if not data:
                idx = self._rand_another()
                continue

            return data

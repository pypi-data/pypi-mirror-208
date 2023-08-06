from __future__ import annotations

from types import ModuleType
from typing import Dict, List, Tuple, Optional, Union
from uuid import UUID

from drb.core.node import DrbNode
from drb.exceptions.core import DrbException
from drb.topics import resolver
from drb.topics.dao import ManagerDao
from drb.topics.topic import DrbTopic
from drb.utils.plugins import get_entry_points
from drb.extractor import Extractor
from drb.extractor.extractor import __factories
import os
import jsonschema
import yaml
import importlib
import logging

_logger = logging.getLogger('DrbImage')
_schema = os.path.join(os.path.dirname(__file__), 'schema.yml')


# FIXME Refactor this method in drb.utils.plugin
def _retrieve_cortex_file(module: ModuleType) -> str:
    """
    Retrieves the metadata cortex file from the given module.

    Parameters:
        module (ModuleType): target module where the cortex metadata file will
                             be search
    Returns:
        str - path to the cortex metadata file
    Raises:
        FileNotFound: If the metadata cortex file is not found
    """
    directory = os.path.dirname(module.__file__)
    path = os.path.join(directory, 'cortex.yml')
    if not os.path.exists(path):
        path = os.path.join(directory, 'cortex.yaml')

    if not os.path.exists(path):
        raise FileNotFoundError(f'File not found: {path}')

    return path


def parse_extractor(data: dict):
    for key, value in data.items():
        return __factories[key](value)


def validate_md_cortex_file(path: str) -> None:
    """
    Checks the given metadata cortex file is valid.

    Parameters:
        path (str): metadata cortex file path

    Raises:
        DrbException: If the given cortex file is not valid
    """
    with open(_schema) as f:
        schema = yaml.safe_load(f)
    f.close()

    with open(path) as file:
        for data in yaml.safe_load_all(file):
            try:
                jsonschema.validate(data, schema)
            except jsonschema.ValidationError as ex:
                file.close()
                raise DrbException(
                    f'Invalid metadata cortex file: {path}') from ex
        file.close()


def _load_image(yaml_data: dict) -> Tuple[UUID, list[Image], str]:
    uuid = UUID(yaml_data['topic'])
    names = list(yaml_data['image'].keys())
    res = []
    for name in names:

        for data in yaml_data['image'][name]['source']:
            if 'extractor' in data.keys():
                extractor = parse_extractor(data['extractor'])
                res.append(Image(name=name,
                                 extractor=extractor,
                                 data=data)
                           )

    return uuid, res, yaml_data.get('default', None)


def _load_all_image() -> Dict[UUID, Tuple[List[Image], str]]:
    """
    Loads all metadata defined in the current Python environment
    with the entry points drb.image.
    """
    entry_point_group = 'drb.image'
    image = {}

    for ep in get_entry_points(entry_point_group):
        try:
            module = importlib.import_module(ep.value)
        except ModuleNotFoundError as ex:
            _logger.warning(f'Invalid DRB Image entry-point {ep}: {ex.msg}')
            continue

        try:
            cortex = _retrieve_cortex_file(module)
            validate_md_cortex_file(cortex)
        except (FileNotFoundError, DrbException) as ex:
            _logger.warning(ex)
            continue

        with open(cortex) as file:
            for data in yaml.safe_load_all(file):
                uuid, img, default = _load_image(data)
                image[uuid] = (img, default)
    return image


class Image:
    def __init__(self, name: str, extractor: Extractor,
                 data: dict = {}):
        self._name = name
        self.extractor = extractor
        self._data = data
        self._node = None

    def __getattr__(self, item):
        if item in self._data.keys():
            return self._data[item]
        raise AttributeError

    @property
    def name(self) -> str:
        """
        Provide the name of the image.
        """
        return self._name

    @property
    def addon_data(self) -> Optional[dict]:
        """
        Provide the raw data of the image addon,
        in the dict format.
        in the dict format.
        """
        return self._data

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, value: DrbNode) -> None:
        self._node = value

    def image_node(self) -> DrbNode:  # DrbImageNode
        """
        Provides the current image as a DrbNode
        """
        return self.extractor.extract(self.node)

    def get_impl(self, impl):
        return self.image_node().get_impl(impl)


class AddonImage:
    @staticmethod
    def images(source) -> List[str]:
        """
        Returns available images list that can be generated
        Parameters:
          source (DrbNode, str, Topic):
        """
        _images = _load_all_image()
        res = []

        if isinstance(source, DrbNode) or isinstance(source, str):
            topic, node = resolver.resolve(source)
        elif isinstance(source, DrbTopic):
            topic = source
        else:
            raise DrbException(
                f"Cannont find any image addon corresponding to {source}")

        if topic.id in _images.keys():
            for e in _images[topic.id][0]:
                res.append(e.name)
        if topic.subClassOf is not None:
            for parent_id in topic.subClassOf:
                if parent_id in _images.keys():
                    res.append(AddonImage.images(
                        ManagerDao().get_drb_topic(parent_id)
                    ))

        return res

    @staticmethod
    def create(node: Union[DrbNode, str],
               image_name: str = None,
               **kwargs) -> Image:
        """
        Create a new image representation on the node
        Parameters:
          node (DrbNode): an image will be generated from that node
          image_name (str): (default ``None``)
        """
        _images = _load_all_image()

        topic, node = resolver.resolve(node)

        try:
            tmp = _images[topic.id]
        except IndexError:
            raise DrbException(f"No descriptor found for node {node.name}")

        options = list(kwargs.keys())
        res = tmp[0]

        if image_name is not None:
            remove = []
            for t in res:
                if t.name != image_name:
                    remove.append(t)
            res = list(set(res) - set(remove))

        if options:
            remove = []
            for opt in options:
                for t in res:
                    try:
                        if t.__getattr__(opt) != kwargs[opt]:
                            remove.append(t)
                    except AttributeError:
                        pass
            res = list(set(res) - set(remove))

        if image_name is None and not kwargs:
            remove = []
            if tmp[1] is not None:
                for t in res:
                    if t.name != tmp[1]:
                        remove.append(t)
                res = list(set(res) - set(remove))

        try:
            res[0].node = node
            return res[0]
        except IndexError:
            raise DrbException(f'No image descriptor found for '
                               f'{image_name}, {kwargs}')

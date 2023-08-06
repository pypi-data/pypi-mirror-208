import unittest

import rasterio
from drb.drivers.image import DrbImageBaseNode
from drb.drivers.netcdf import DrbNetcdfNode
from drb.exceptions.core import DrbException
from drb.topics import resolver

from drb.image import AddonImage
from drb.image.image import Image


def my_method(node):
    return DrbImageBaseNode(node)


def my_method_2(node):
    return node


class TestImageAddon(unittest.TestCase):
    S1 = 'tests/resources/S1A_IW_SLC__1SDV_20230131T104608_' \
         '20230131T104643_047026_05A40B_2AFB.SAFE'
    S2 = 'tests/resources/S2A_MSIL2A_20230131T075141_N0509_R135_' \
         'T36MYD_20230131T131152.SAFE'
    S5 = 'tests/resources/S5P_NRTI_L2__AER_AI_20230203T111306_' \
         '20230203T111806_27510_03_020400_20230203T130053.nc'
    S1_LO = 'tests/resources/S1A_IW_RAW__0SDH_20220201T1017' \
            '15_20220201T101734_041718_04F6C6_A26E.SAFE'

    def test_constant(self):
        node = resolver.create(self.S1)
        extract = AddonImage.create(node)

        self.assertIsNotNone(extract)
        self.assertIsInstance(extract, Image)
        self.assertEqual('quicklook', extract.name)

        base_node = extract.image_node()
        self.assertIsNotNone(base_node)
        self.assertIsInstance(base_node, DrbImageBaseNode)

    def test_python(self):
        node = resolver.create(self.S2)

        extract = AddonImage.create(node)
        self.assertIsNotNone(extract)
        self.assertIsInstance(extract, Image)
        self.assertEqual('TrueColorImage', extract.name)

        base_node = extract.image_node()
        self.assertIsNotNone(base_node)
        self.assertIsInstance(base_node, DrbImageBaseNode)

    def test_script(self):
        node = resolver.create(self.S5)

        extract = AddonImage.create(node)
        self.assertIsNotNone(extract)
        self.assertIsInstance(extract, Image)
        self.assertEqual('index_354_388', extract.name)
        self.assertEqual(310, extract.frequency)

        base_node = extract.image_node()
        self.assertIsNotNone(base_node)
        self.assertIsInstance(base_node, DrbImageBaseNode)

    def test_resolutions(self):
        node = resolver.create(self.S1_LO)

        extract = AddonImage.create(node, resolution='10m')
        self.assertIsNotNone(extract)
        self.assertIsInstance(extract, Image)
        self.assertEqual('bo4', extract.name)
        self.assertEqual('10m', extract.resolution)
        self.assertEqual([205, 305], extract.frequency)

        extract = AddonImage.create(node, resolution='20m')
        self.assertIsNotNone(extract)
        self.assertIsInstance(extract, Image)
        self.assertEqual('bo4', extract.name)
        self.assertEqual('20m', extract.resolution)
        self.assertEqual([205, 305], extract.frequency)

    def test_freq(self):
        node = resolver.create(self.S5)

        extract = AddonImage.create(node, frequency=[270, 300])
        self.assertIsNotNone(extract)
        self.assertIsInstance(extract, Image)
        self.assertEqual('index_340_380', extract.name)
        self.assertEqual([270, 300], extract.frequency)

        extract = AddonImage.create(node, frequency=310)
        self.assertIsNotNone(extract)
        self.assertIsInstance(extract, Image)
        self.assertEqual('index_354_388', extract.name)
        self.assertEqual(310, extract.frequency)

        with self.assertRaises(DrbException):
            AddonImage.create(node, frequency=320)

    def test_filter(self):
        node = resolver.create(self.S5)

        extract = AddonImage.create(node,
                                    image_name='index_340_380',
                                    freq='290')
        self.assertIsNotNone(extract)
        self.assertIsInstance(extract, Image)
        self.assertEqual('index_340_380', extract.name)
        self.assertEqual([270, 300], extract.frequency)

        with self.assertRaises(DrbException):
            AddonImage.create(node, image_name='index_354_388',
                              frequency='290')

    def test_default(self):
        node = resolver.create(self.S5)

        extract = AddonImage.create(node, image_name='index_340_380')
        self.assertIsNotNone(extract)
        self.assertIsInstance(extract, Image)
        self.assertEqual('index_340_380', extract.name)
        self.assertEqual([270, 300], extract.frequency)

        base_node = extract.image_node()
        self.assertIsNotNone(base_node)
        self.assertIsInstance(base_node, DrbNetcdfNode)

        with self.assertRaises(DrbException):
            AddonImage.create(node, image_name='Wrong_name')

    def test_load_images(self):
        s1 = AddonImage.images(self.S1)
        self.assertIsNotNone(s1)
        self.assertIsInstance(s1, list)
        self.assertEqual(len(s1), 1)
        self.assertEqual(s1[0], 'quicklook')

        topic, node = resolver.resolve(self.S1)

        s1 = AddonImage.images(node)
        self.assertIsNotNone(s1)
        self.assertIsInstance(s1, list)
        self.assertEqual(len(s1), 1)
        self.assertEqual(s1[0], 'quicklook')

        s1 = AddonImage.images(topic)
        self.assertIsNotNone(s1)
        self.assertIsInstance(s1, list)
        self.assertEqual(len(s1), 1)
        self.assertEqual(s1[0], 'quicklook')

        with self.assertRaises(DrbException):
            AddonImage.images(1)

        with self.assertRaises(TypeError):
            AddonImage.images()

    def test_simpl_usage(self):
        extract = AddonImage.create(self.S1)
        self.assertIsNotNone(extract)
        self.assertIsInstance(extract, Image)
        impl = extract.get_impl(rasterio.DatasetReader)
        self.assertIsInstance(impl, rasterio.io.DatasetReader)
        self.assertEqual(
            impl,
            extract.image_node().get_impl(rasterio.DatasetReader)
        )

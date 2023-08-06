import shutil

import unittest
import uuid
import os
import tempfile
import tarfile
import drb.topics.resolver as resolver
from drb.topics.dao import ManagerDao


class TestLandsat8Topic(unittest.TestCase):
    # from GAEL Systems dataset ref
    data = {
            "LC81820462016026LBG00.tar.gz",
            "LC81830602017019LBG00.tar.gz",
            "LC08_L1GT_222116_20200301_20200313_01_T2.tar.gz",
            "LC08_L1GT_108023_20210322_20210322_01_RT.tar.gz",
            "LC08_L1TP_003006_20180602_20180615_01_T1.tar.gz",
            "LO08_L1TP_108024_20201114_20201119_01_T1.tar.gz",
            "LO08_L1TP_108014_20201114_20201119_01_T2.tar.gz",
            "LO08_L1GT_108063_20201114_20201119_01_T2.tar.gz",
            "LO08_L1GT_108028_20201114_20201119_01_T2.tar.gz",
            "LT08_L1GT_016212_20210317_20210317_01_RT.tar.gz",
            "LT08_L1GT_019212_20210322_20210322_01_RT.tar.gz",
            "LC08_L1TP_101026_20211202_20211202_02_RT.tar",
            "LC08_L1TP_101077_20211202_20211202_02_RT.tar",
            "LC08_L1TP_092078_20211203_20211203_02_RT.tar",
            "LC08_L1TP_117041_20211202_20211202_02_RT.tar",
    }
    data_dir = None
    topic_labels = {
        uuid.UUID('d6ec274f-d84a-499d-923a-5116c1b96655'):
            'Landsat-8 Level-1 GeoTIFF Product',
        uuid.UUID('10e14810-3060-4f55-99e7-3a84e2947343'):
            'Landsat-8 Level-1 GeoTIFF Collection 1 Product',
        uuid.UUID('460f7ffa-3ebb-4122-8ce3-53d54432727b'):
            'Landsat-8 Level-1 GeoTIFF Collection 2 Product',
    }

    @classmethod
    def setUpClass(cls) -> None:
        cls.data_dir = tempfile.mkdtemp(prefix='landsat8', suffix='dataset')
        for name in cls.data:
            cls.generate_empty_tar_file(os.path.join(cls.data_dir, name))

    @classmethod
    def tearDownClass(cls) -> None:
        if os.path.isdir(cls.data_dir):
            shutil.rmtree(cls.data_dir)

    @staticmethod
    def generate_empty_tar_file(name: str):
        path = os.path.join(tempfile.gettempdir(), name)
        mode = "w|gz" if name.lower().endswith('gz') else "w|"
        tar = tarfile.open(path, mode)
        tar.close()
        return path

    def test_topic_loading(self):
        topic_loader = ManagerDao()
        for key in self.topic_labels.keys():
            topic = topic_loader.get_drb_topic(key)
            self.assertEqual(self.topic_labels[key], topic.label)

    def test_topic_resolution(self):
        topics = ManagerDao()

        # Landsat-8 product before 2017
        ex_topic = topics.get_drb_topic(
            uuid.UUID('d6ec274f-d84a-499d-923a-5116c1b96655'))
        for n in filter(lambda x: x[2] == '8', self.data):
            ac_topic, node = resolver.resolve(os.path.join(self.data_dir, n))
            self.assertEqual(ex_topic.id, ac_topic.id)

        # Collection 1
        ex_topic = topics.get_drb_topic(
            uuid.UUID('10e14810-3060-4f55-99e7-3a84e2947343'))
        for n in filter(lambda x: len(x) > 37 and x[35:37] == '01', self.data):
            ac_topic, node = resolver.resolve(os.path.join(self.data_dir, n))
            self.assertEqual(ex_topic.id, ac_topic.id)

        # Collection 2
        ex_topic = topics.get_drb_topic(
            uuid.UUID('460f7ffa-3ebb-4122-8ce3-53d54432727b'))
        for n in filter(lambda x: len(x) > 37 and x[35:37] == '02', self.data):
            ac_topic, node = resolver.resolve(os.path.join(self.data_dir, n))
            self.assertEqual(ex_topic.id, ac_topic.id)

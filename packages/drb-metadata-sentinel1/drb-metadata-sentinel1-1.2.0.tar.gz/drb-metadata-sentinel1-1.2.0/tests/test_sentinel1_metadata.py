import json
import os
import unittest
import drb.topics.resolver as resolver
from drb.core.node import DrbNode
from drb.metadata import DrbMetadataResolver


class TestSentinel1Metadata(unittest.TestCase):
    md_resolver: DrbMetadataResolver = None
    data_dir: str = None
    expected: dict = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.md_resolver = DrbMetadataResolver()
        cls.data_dir = os.path.join(os.path.dirname(__file__), 'resources')
        with open(os.path.join(cls.data_dir, 'expected.json')) as file:
            cls.expected = json.load(file)

    def _check_metadata(self, expected: dict, node: DrbNode) -> tuple:
        """
        Checks if the given node have all expected metadata and checks also
        their values.

        Parameters:
            expected (dict):
            node (DrbNode):
        Returns:
             tuple(bool, dict): True and an empty dict if all actual metadata
                                are equal to expected metadata, otherwise False
                                and a diff report dict.
        """
        metadata = self.md_resolver.get_metadata(node)
        report = {}
        for key, value in expected.items():
            if key not in metadata.keys():
                report[key] = 'metadata missing'
                continue
            actual = metadata[key].extract(node)
            if value != actual:
                report[key] = {'expected': value, 'actual': actual}
        return len(report) == 0, report

    def test_sentinel1_level0_product_metadata(self):
        product = "S1A_IW_RAW__0SDV_20200414T160317_20200414T160350_032125_" \
                  "03B6B7_16FD.SAFE"
        node = resolver.create(os.path.join(self.data_dir, product))
        rc, report = self._check_metadata(self.expected[node.name], node)
        self.assertTrue(rc, report)

    def test_sentinel1_level1_product_metadata(self):
        product = "S1A_IW_SLC__1SDV_20190508T103032_20190508T103100_027135_" \
                  "030EFE_7601.SAFE"
        node = resolver.create(os.path.join(self.data_dir, product))
        rc, report = self._check_metadata(self.expected[node.name], node)
        self.assertTrue(rc, report)

    def test_sentinel1_level2_product_metadata(self):
        product = "S1A_WV_OCN__2SSV_20220602T125218_20220602T131729_043484_" \
                  "053129_C039.SAFE"
        node = resolver.create(os.path.join(self.data_dir, product))
        rc, report = self._check_metadata(self.expected[node.name], node)
        self.assertTrue(rc, report)

    def test_sentinel1_auxiliary_product(self):
        product = "S1B_AUX_PP1_V20160422T000000_G20190626T095204.SAFE"
        node = resolver.create(os.path.join(self.data_dir, product))
        rc, report = self._check_metadata(self.expected[node.name], node)
        self.assertTrue(rc, report)

    def test_sentinel1_eof_auxiliary_product(self):
        product = "S1A_OPER_AUX_POEORB_OPOD_20181101T120839_" \
                  "V20181011T225942_20181013T005942.EOF"
        node = resolver.create(os.path.join(self.data_dir, product))
        rc, report = self._check_metadata(self.expected[node.name], node)
        self.assertTrue(rc, report)

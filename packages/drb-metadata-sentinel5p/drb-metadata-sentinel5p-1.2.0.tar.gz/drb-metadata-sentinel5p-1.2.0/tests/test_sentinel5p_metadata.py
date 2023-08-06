import json
import os.path
import unittest
import drb.topics.resolver as resolver
from drb.core.node import DrbNode
from drb.metadata import DrbMetadataResolver


class TestSentinel5Metadata(unittest.TestCase):
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
            if key == 'resourceAbstract':
                if value not in actual:
                    report[key] = {'expected (start)': value,
                                   'actual': actual[:50]}
            elif value != actual:
                report[key] = {'expected': value, 'actual': actual}
        return len(report) == 0, report

    def test_sentinel5_L2_CH4_product_metadata(self):
        product = "S5P_OFFL_L2__CH4____20210718T031151_20210718T045321_" \
                  "19490_02_020200_20210719T200158.nc"
        node = resolver.create(os.path.join(self.data_dir, product))
        rc, report = self._check_metadata(self.expected[node.name], node)
        self.assertTrue(rc, report)

    def test_sentinel5_L2_CO_product_metadata(self):
        product = "S5P_OFFL_L2__CO_____20210715T040904_20210715T055034_" \
                  "19448_02_020200_20210716T175757.nc"
        node = resolver.create(os.path.join(self.data_dir, product))
        rc, report = self._check_metadata(self.expected[node.name], node)
        self.assertTrue(rc, report)

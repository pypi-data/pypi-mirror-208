import os
import uuid
import yaml
import json
import unittest
import xmldiff.main
import xmldiff.formatting
import drb.topics.resolver as resolver
from drb.core.node import DrbNode
from drb.metadata import DrbMetadataResolver
from drb.topics.dao import ManagerDao
from drb.topics.topic import DrbTopic


def is_a(topic: DrbTopic, parent_topic: DrbTopic) -> bool:
    return ManagerDao().is_subclass(topic, parent_topic)


class TestSentinel3Metadata(unittest.TestCase):
    dir_path = None
    expected = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.dir_path = os.path.join(os.path.dirname(__file__), 'resources')
        path = os.path.join(cls.dir_path, 'expected.yml')
        with open(path) as expected_file:
            cls.expected = yaml.safe_load(expected_file)

    def check_metadata(self, expected: dict, actual: dict) -> None:
        report = {}
        for expected_key, expected_value in expected.items():
            if expected_key not in actual:
                report[expected_key] = "Missing metadata"
            elif expected_key == 'coordinates':
                diff = xmldiff.main.diff_texts(
                    expected_value,
                    actual[expected_key])
                if diff:
                    report[expected_key] = {
                        'expected': expected_value,
                        'actual': actual[expected_key],
                        'diff': [str(e) for e in diff],
                    }
            else:
                if expected_key in actual:
                    if expected_value != actual[expected_key]:
                        report[expected_key] = {
                            'expected': expected_value,
                            'actual': actual[expected_key]
                        }
        if report:
            self.fail(f'Invalid metadata: {json.dumps(report, indent=2)}')

    def validate_metadata(self, node: DrbNode):
        md = {
            k: v.extract(node)
            for k, v in DrbMetadataResolver().get_metadata(node).items()
        }
        self.check_metadata(self.expected[node.name], md)

    def test_auxiliary_product(self):
        prd = "S3__SR_2_SURFAX_20160216T000000_20991231T235959_" \
                  "20161010T120000___________________MPC_O_AL_002.SEN3"
        expected_topic_id = uuid.UUID("811df024-1d70-41c6-b316-f33de2976a17")
        topic, node = resolver.resolve(os.path.join(self.dir_path, prd))
        self.assertTrue(is_a(
            topic,
            ManagerDao().get_drb_topic(expected_topic_id)
        ))
        self.validate_metadata(node)

    def test_level0_product(self):
        prd = "S3A_DO_0_NAV____20200107T021423_20200107T035653_" \
                  "20200107T040728_6149_053_260______LN3_O_AL_002.SEN3"
        expected_topic_id = uuid.UUID("6ee38ad7-14b9-4d94-a412-2bf8cc7d79c1")
        topic, node = resolver.resolve(os.path.join(self.dir_path, prd))
        self.assertTrue(is_a(
            topic,
            ManagerDao().get_drb_topic(expected_topic_id)
        ))
        self.validate_metadata(node)

    def test_level1_sral_product(self):
        product = "S3A_SR_1_CAL____20200107T010933_20200107T010946_" \
                  "20200107T022626_0013_053_259______LN3_O_NR_003.SEN3"
        expected_topic_id = uuid.UUID("b684eb6b-b3ca-49f6-bcfc-331f40753c48")
        topic, node = resolver.resolve(os.path.join(self.dir_path, product))
        self.assertTrue(is_a(
            topic,
            ManagerDao().get_drb_topic(expected_topic_id)
        ))
        self.validate_metadata(node)

    def test_level1_slstr_product(self):
        product = "S3A_SL_1_RBT____20200105T071934_20200105T072234_" \
                  "20200106T114858_0179_053_234_4320_LN2_O_NT_003.SEN3"
        expected_topic_id = uuid.UUID("a34c9628-81d6-4255-89f7-b6ea327fcf56")
        topic, node = resolver.resolve(os.path.join(self.dir_path, product))
        self.assertTrue(is_a(
            topic,
            ManagerDao().get_drb_topic(expected_topic_id)
        ))
        self.validate_metadata(node)

    def test_level1_olci_product(self):
        product = "S3A_OL_1_RAC____20200111T131433_20200111T131626_" \
                  "20200111T160343_0113_053_323______LN1_O_NR_002.SEN3"
        expected_topic_id = uuid.UUID("bdac9498-0b0d-4d12-b2d9-194a49c47d63")
        topic, node = resolver.resolve(os.path.join(self.dir_path, product))
        self.assertTrue(is_a(
            topic,
            ManagerDao().get_drb_topic(expected_topic_id)
        ))
        self.validate_metadata(node)

    def test_level2_olci_product(self):
        product = "S3A_OL_2_LFR____20200105T070134_20200105T070434_" \
                  "20200106T115031_0179_053_234_3240_LN1_O_NT_002.SEN3"
        expected_topic_id = uuid.UUID("846ce2b7-9fa0-4072-bfe3-a9e4a53b275c")
        topic, node = resolver.resolve(os.path.join(self.dir_path, product))
        self.assertTrue(is_a(
            topic,
            ManagerDao().get_drb_topic(expected_topic_id)
        ))
        self.validate_metadata(node)

    def test_synergy_product(self):
        product = "S3A_SY_2_V10____20191216T110000_20191226T110000_" \
                  "20200105T113727_AFRICA____________LN2_O_NT_002.SEN3"
        expected_topic_id = uuid.UUID("d0d11702-c384-49ba-a029-ba59bba89946")
        topic, node = resolver.resolve(os.path.join(self.dir_path, product))
        self.assertTrue(is_a(
            topic,
            ManagerDao().get_drb_topic(expected_topic_id)
        ))
        self.validate_metadata(node)

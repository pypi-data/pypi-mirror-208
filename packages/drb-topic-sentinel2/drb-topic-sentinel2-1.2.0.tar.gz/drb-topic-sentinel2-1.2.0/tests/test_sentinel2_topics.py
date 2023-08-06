import os
import unittest

from tests.topic_test import TopicTest


class TestSentinel2Topics(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.topic = TopicTest(os.path.join(os.path.dirname(__file__),
                                           'resources',
                                           'sentinel2.yml'
                                           ))

    def test_sentinel2_signature_test(self):
        self.topic.check(self)

    def test_sentinel2_mandatory(self):
        self.topic.mandatory_field(self)

    def test_sentinel2_optional(self):
        self.topic.optional_field(self)

    def test_match_nodes(self):
        self.topic.match_good_nodes(self)

    def test_not_match_nodes(self):
        self.topic.match_bad_nodes(self)

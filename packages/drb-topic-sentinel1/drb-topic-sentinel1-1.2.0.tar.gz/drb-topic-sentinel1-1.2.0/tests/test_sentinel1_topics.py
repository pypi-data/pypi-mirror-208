import os
import unittest

from tests.topic_test import TopicTest


class TestSentinel1Topics(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.topic = TopicTest(os.path.join(os.path.dirname(__file__),
                                           'resources',
                                           'sentinel1.yml'
                                           ))

    def test_sentinel1_signature_test(self):
        self.topic.check(self)

    def test_sentinel1_mandatory(self):
        self.topic.mandatory_field(self)

    def test_sentinel1_optional(self):
        self.topic.optional_field(self)

    def test_match_nodes(self):
        self.topic.match_good_nodes(self)

    def test_not_match_nodes(self):
        self.topic.match_bad_nodes(self)

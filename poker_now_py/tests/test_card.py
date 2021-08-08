import unittest
from unittest import TestCase
from card import EmojiCard, Card

class TestCard(TestCase):
    def test_emoji_card(self):
        self.assertEqual("2♥", EmojiCard.h2.value)
        self.assertEqual("A♥", EmojiCard.hA.value)
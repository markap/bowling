# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from api import models

class AddScoreTest(TestCase):
    def setUp(self):
        self.game = models.Game.objects.create()

    def test_add_score(self):
        self.assertEqual(self.game.frames.count(), 0)
        self.game.add_score(6)
        self.assertEqual(self.game.frames.count(), 1)
        self.game.add_score(4)
        self.assertEqual(self.game.frames.count(), 1)
        self.assertTrue(self.game.frames.last().is_spare)
        self.game.add_score(10)
        self.assertEqual(self.game.frames.count(), 2)
        self.game.add_score(3)
        self.assertEqual(self.game.frames.count(), 3)
        self.game.add_score(4)
        self.assertEqual(self.game.frames.count(), 3)
        self.assertEqual(self.game.frames.last().score_one, 3)
        self.assertEqual(self.game.frames.last().score_two, 4)
        self.game.add_score(3)
        self.assertEqual(self.game.frames.count(), 4)

class CalculateScoreTest(TestCase):
	def setUp(self):
		self.game = models.Game.objects.create()

	def test_calculate_lame(self):
		self.game.add_score(3)
		self.assertEqual(self.game.calculate_score(), 3)
		self.game.add_score(5)
		self.assertEqual(self.game.calculate_score(), 8)

		self.game.add_score(5)
		self.game.add_score(5)
		self.assertEqual(self.game.calculate_score(), 18)

		self.game.add_score(10)
		self.assertEqual(self.game.calculate_score(), 38)

		self.game.add_score(10)
		self.assertEqual(self.game.calculate_score(), 58)

		self.game.add_score(0)
		self.game.add_score(3)
		self.assertEqual(self.game.calculate_score(), 64)
        



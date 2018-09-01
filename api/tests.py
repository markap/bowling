# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from api import models

class AddScoreTest(TestCase):
    def setUp(self):
        self.game = models.Game.objects.create()

   
    # helper function, mainly to test the various
    # cases how a game can end
    def _create_strike_frames(self, count):
        for i in xrange(count):
            self.game.add_score(10)

    # helper function to check frames score
    def _assert_frames(self, frames, expected):
        for index, frame in enumerate(frames):
            print "check frame %s - %s" % (frame.score, expected[index])
            self.assertEqual(frame.score, expected[index])


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

    def test_invalid_score(self):
        self.assertRaises(models.InvalidScoreException,
                          self.game.add_score, 11)

        self.assertRaises(models.InvalidScoreException,
                          self.game.add_score, -1)

        self.assertRaises(models.InvalidScoreException,
                          self.game.add_score, 0.5)

        self.assertRaises(models.InvalidScoreException,
                          self.game.add_score, "hihi")

        self.assertRaises(models.InvalidScoreException,
                          self.game.add_score, None)

    def test_invalid_score_more_than_10(self):
        self.game.add_score(6)
        self.assertRaises(models.InvalidScoreException,
                          self.game.add_score, 5)
        self.game.add_score(4)

    def test_invalid_score_end_of_game(self):
        self._create_strike_frames(9)
        self.assertFalse(self.game.is_over)
        self.assertEqual(self.game.frames.count(), 9)

        self.game.add_score(3)
        self.assertRaises(models.InvalidScoreException,
                          self.game.add_score, 8)

        self.assertFalse(self.game.is_over)
        self.game.add_score(7)
        self.game.add_score(7)

        self.assertEqual(self.game.frames.count(), 10)
        self.assertTrue(self.game.is_over)

    def test_valid_score_end_of_game_strike(self):
        self._create_strike_frames(10)
        self.assertFalse(self.game.is_over)
        self.assertEqual(self.game.frames.count(), 10)

        self.game.add_score(7)
        self.game.add_score(7)
        self.assertTrue(self.game.is_over)

    def test_lame_finish(self):
        self._create_strike_frames(9)
        self.assertFalse(self.game.is_over)
        self.assertEqual(self.game.frames.count(), 9)

        self.game.add_score(3)
        self.assertEqual(self.game.frames.count(), 10)
        self.game.add_score(4)
        self.assertEqual(self.game.frames.count(), 10)

        score, frames = self.game.calculate_score()
        self.assertEqual(score, 257)

        self._assert_frames(
            frames, 
            [30, 60, 90, 120, 150, 180, 210, 233, 250, 257]
        )

        self.assertRaises(models.GameOverException, self.game.add_score, 4)
        self.assertTrue(self.game.is_over)

    def test_spare_finish(self):
        self._create_strike_frames(9)

        self.game.add_score(3)
        self.assertEqual(self.game.frames.count(), 10)
        self.game.add_score(7)
        self.assertEqual(self.game.frames.count(), 10)
        self.game.add_score(5)
        self.assertEqual(self.game.frames.count(), 10)

        score, frames = self.game.calculate_score()
        self.assertEqual(score, 268)
        self._assert_frames(
            frames,
            [30, 60, 90, 120, 150, 180, 210, 233, 253, 268]
        )

        self.assertRaises(models.GameOverException, self.game.add_score, 10)
        self.assertTrue(self.game.is_over)

    def test_perfect_game(self):
        self.game.add_score(10)
        self.game.add_score(10)
        self.game.add_score(10)
        self.game.add_score(10)
        self.game.add_score(10)
        self.game.add_score(10)
        self.game.add_score(10)
        self.game.add_score(10)
        self.game.add_score(10)
        self.game.add_score(10)
        self.assertEqual(self.game.frames.count(), 10)
        self.game.add_score(10)
        self.assertEqual(self.game.frames.count(), 10)
        self.game.add_score(10)
        self.assertEqual(self.game.frames.count(), 10)

        score, frames = self.game.calculate_score()
        self.assertEqual(score, 300)
        self._assert_frames(
            frames, 
            [30, 60, 90, 120, 150, 180, 210, 240, 270, 300]
        )

        self.assertRaises(models.GameOverException, self.game.add_score, 10)

    def test_calculate_without_frame(self):
        score, frames = self.game.calculate_score()
        self.assertEqual(score, 0)
        self.assertEqual(len(frames), 0)
       
       
    def test_random_game(self): 
        self.game.add_score(2)
        self.game.add_score(8)
        score, frames = self.game.calculate_score()
        self.assertEqual(score, 10)
        self._assert_frames(
            frames,
            [10]
        )
        
        self.game.add_score(2)
        self.game.add_score(8)
   
        self.game.add_score(6)
        self.game.add_score(2)
        score, frames = self.game.calculate_score()
        self.assertEqual(score, 36)
        self._assert_frames(
            frames,
            [12, 28, 36]
        )

        self.game.add_score(10)
        score, frames = self.game.calculate_score()
        self.assertEqual(score, 46)
        self._assert_frames(
            frames,
            [12, 28, 36, 46]
        )
   
        self.game.add_score(4)
        self.game.add_score(5)
        score, frames = self.game.calculate_score()
        self.assertEqual(score, 64)
        self._assert_frames(
            frames,
            [12, 28, 36, 55, 64]
        )

        self.game.add_score(3)
        self.game.add_score(7)
        score, frames = self.game.calculate_score()
        self.assertEqual(score, 74)
        self._assert_frames(
            frames,
            [12, 28, 36, 55, 64, 74]
        )

        self.game.add_score(10)
        score, frames = self.game.calculate_score()
        self.assertEqual(score, 94)
        self._assert_frames(
            frames,
            [12, 28, 36, 55, 64, 84, 94]
        )

        self.game.add_score(0)
        self.game.add_score(0)
        score, frames = self.game.calculate_score()
        self.assertEqual(score, 94)
        self._assert_frames(
            frames,
            [12, 28, 36, 55, 64, 84, 94, 94]
        )

        self.game.add_score(5)
        self.game.add_score(5)
        score, frames = self.game.calculate_score()
        self.assertEqual(score, 104)
        self._assert_frames(
            frames,
            [12, 28, 36, 55, 64, 84, 94, 94, 104]
        )

        self.game.add_score(4)
        self.assertFalse(self.game.is_over)
        self.game.add_score(3)
        score, frames = self.game.calculate_score()
        self.assertEqual(score, 115)
        self._assert_frames(
            frames,
            [12, 28, 36, 55, 64, 84, 94, 94, 108, 115]
        )

        self.assertTrue(self.game.is_over)


    def test_horrible_game(self):
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        self.game.add_score(0)
        score, _ = self.game.calculate_score()
        self.assertEqual(score, 0)
        self.assertTrue(self.game.is_over)


    def test_empty_frame(self): 

        self.game.add_score(10)
        self.game.add_score(0)
        self.game.add_score(0)
        score, frames = self.game.calculate_score()
        self.assertEqual(score, 10)
        self._assert_frames(
            frames,
            [10, 10]
        )
        self.assertEqual(self.game.frames.count(), 2)


        self.game.add_score(5)
        self.game.add_score(5)
        score, frames = self.game.calculate_score()
        self.assertEqual(self.game.frames.count(), 3)
        self.assertEqual(score, 20)
        self._assert_frames(
            frames,
            [10, 10, 20]
        )


class CalculateScoreTest(TestCase):
	def setUp(self):
		self.game = models.Game.objects.create()

	def test_calculate_lame(self):
		self.game.add_score(3)
		self.assertEqual(self.game.calculate_score()[0], 3)
		self.game.add_score(5)
		self.assertEqual(self.game.calculate_score()[0], 8)

		self.game.add_score(5)
		self.game.add_score(5)
		self.assertEqual(self.game.calculate_score()[0], 18)

		self.game.add_score(10)
		self.assertEqual(self.game.calculate_score()[0], 38)

		self.game.add_score(10)
		self.assertEqual(self.game.calculate_score()[0], 58)

		self.game.add_score(0)
		self.game.add_score(3)
		self.assertEqual(self.game.calculate_score()[0], 64)
        



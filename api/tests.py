# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from rest_framework.test import APIClient

from api import models
from api import views

class CreateGameViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_game(self):
        response = self.client.post('/api/new/', format='json')

        self.assertTrue('game_id' in response.data)
        game = models.Game.objects.get(pk=response.data.get('game_id'))
        self.assertTrue(game is not None)
        self.assertEqual(response.status_code, 200)

    def test_create_game_get_not_allowed(self):
        response = self.client.get('/api/new/')
        self.assertEqual(response.status_code, 405)

class GameResultTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.game = models.Game.objects.create()

    def test_game_does_not_exist(self):
        response = self.client.post('/api/result/', {'game_id': 99}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('error'),
                         views.ERROR_GAME_DOES_NOT_EXIST)

    def test_empty_game(self):
        response = self.client.post('/api/result/', {'game_id': self.game.id}, format='json')

        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['game_id'], self.game.id)
        self.assertEqual(data['score'], 0)
        self.assertEqual(data['is_over'], False)
        self.assertEqual(len(data['frames']), 0)

    def test_first_legs_game(self):
        self.game.add_score(5)
        self.game.add_score(5)
        self.game.add_score(10)
        self.game.add_score(0)
        self.game.add_score(3)
        response = self.client.post('/api/result/', {'game_id': self.game.id}, format='json')

        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['game_id'], self.game.id)
        self.assertEqual(data['score'], 36)
        self.assertEqual(data['is_over'], False)
        self.assertEqual(len(data['frames']), 3)
        
        frame = data.get('frames')[0]
        self.assertEqual(frame['score_one'], 5)
        self.assertEqual(frame['score_two'], 5)
        self.assertEqual(frame['score'], 20)
        self.assertEqual(frame['is_strike'], False)
        self.assertEqual(frame['is_spare'], True)

        frame = data.get('frames')[1]
        self.assertEqual(frame['score_one'], 10)
        self.assertEqual(frame['score_two'], None)
        self.assertEqual(frame['score'], 33)
        self.assertEqual(frame['is_strike'], True)
        self.assertEqual(frame['is_spare'], False)

        frame = data.get('frames')[2]
        self.assertEqual(frame['score_one'], 0)
        self.assertEqual(frame['score_two'], 3)
        self.assertEqual(frame['score'], 36)
        self.assertEqual(frame['is_strike'], False)
        self.assertEqual(frame['is_spare'], False)

    def test_get_not_allowed(self):
        response = self.client.get('/api/result/', {'game_id': self.game.id})
        self.assertEqual(response.status_code, 405)

    def test_perfect_game(self):
        for _ in xrange(12):
            self.game.add_score(10)
        response = self.client.post('/api/result/', {'game_id': self.game.id}, format='json')

        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['game_id'], self.game.id)
        self.assertEqual(data['score'], 300)
        self.assertEqual(data['is_over'], True)
        self.assertEqual(len(data['frames']), 10)

        frame = data.get('frames')[-1]
        self.assertEqual(frame['score_one'], 10)
        self.assertEqual(frame['score_two'], 10)
        self.assertEqual(frame['score_three'], 10)
        self.assertEqual(frame['score'], 300)
        self.assertEqual(frame['is_strike'], True)
        self.assertEqual(frame['is_spare'], False)


class AddScoreTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.game = models.Game.objects.create()

    def test_add_score(self):
        response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 5}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(hasattr(response, 'error'))
        self.assertEqual(self.game.frames.last().score_one, 5)

        response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 3}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(hasattr(response, 'error'))
        self.assertEqual(self.game.frames.last().score_two, 3)

        response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 5}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.game.frames.last().score_one, 5)
        self.assertFalse(hasattr(response, 'error'))
        self.assertEqual(self.game.frames.count(), 2)

        response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 5}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.game.frames.last().score_two, 5)
        self.assertFalse(hasattr(response, 'error'))
        self.assertEqual(self.game.frames.count(), 2)

    def test_add_score_strike(self):
        response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 10}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(hasattr(response, 'error'))
        self.assertEqual(self.game.frames.last().score_one, 10)

        response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 10}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(hasattr(response, 'error'))
        self.assertEqual(self.game.frames.last().score_one, 10)

        self.assertEqual(self.game.frames.count(), 2)

    def test_add_score_miss(self):
        response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 0}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(hasattr(response, 'error'))
        self.assertEqual(self.game.frames.last().score_one, 0)

        response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 0}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.game.frames.last().score_one, 0)
        self.assertFalse(hasattr(response, 'error'))
        self.assertEqual(self.game.frames.count(), 1)

        response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 0}, format='json')
        self.assertEqual(self.game.frames.count(), 2)

    def test_add_invalid_score(self):
        response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 11}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('error'),
                         models.InvalidScoreException.message)

        response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 0.5}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('error'),
                         models.InvalidScoreException.message)

        response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 5}, format='json')
        response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 6}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('error'),
                         models.InvalidScoreException.message)


    def test_add_score_game_over(self):
        for _ in xrange(12):
            response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 10}, format='json')
        response = self.client.post('/api/add/', {'game_id': self.game.id, 'score': 10}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('error'),
                         models.GameOverException.message)

    def test_add_score_game_does_not_exist(self):
        response = self.client.post('/api/add/', {'game_id': 99, 'score': 10}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get('error'),
                         views.ERROR_GAME_DOES_NOT_EXIST)
        

    def test_get_not_allowed(self):
        response = self.client.get('/api/add/', {'game_id': self.game.id, 'score': 10})
        self.assertEqual(response.status_code, 405)

class ModelTest(TestCase):
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
        



# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class GameOverException(Exception):
    message = "The Game is already finished"


class InvalidScoreException(Exception):
    message = "Invalid score."


MAX_SCORE = 10
MIN_SCORE = 0


class Frame(models.Model):
    game = models.ForeignKey('Game', related_name='frames')
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    is_spare = models.BooleanField(default=False)
    is_strike = models.BooleanField(default=False)
    is_last_frame = models.BooleanField(default=False)

    score_one = models.IntegerField(null=True, blank=True)
    score_two = models.IntegerField(null=True, blank=True)
    score_three = models.IntegerField(null=True, blank=True)

    def as_dict(self):
        return {'frame_id': self.id,
                'is_spare': self.is_spare,
                'is_strike': self.is_strike,
                'is_last_frame': self.is_last_frame,
                'score': self.score,
                'score_one': self.score_one,
                'score_two': self.score_two,
                'score_three': self.score_three
        }

    def get_score_one(self):
        return self.score_one or 0

    def get_frame_score(self):
        return sum([self.score_one or 0,
                    self.score_two or 0,
                    self.score_three or 0])

    def get_frame_score_for_strike(self):
        return sum([self.score_one or 0,
                    self.score_two or 0])

    def is_closed(self):
        return not self.is_last_frame and (self.is_strike or self._is_two_times_played())

    def _is_two_times_played(self):
        return self.score_one is not None and self.score_two is not None


class Game(models.Model):
    is_over = models.BooleanField(default=False)

    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def as_dict(self, score=0):
        return {
            'game_id': self.id,
            'is_over': self.is_over,
            'score': score
        }

    def add_score(self, score):
        if self.is_over:
            raise GameOverException()

        if self._is_invalid_score(score):
            raise InvalidScoreException()

        prev_frame = self.frames.last()

        # there is no frame yet 
        # or the previous frame is already closed, 
        if prev_frame is None or (prev_frame and prev_frame.is_closed()): 
            self._create_new_frame(score)

        # we are playing in the last frame and we have either a spare or a strike
        elif prev_frame.is_last_frame and (prev_frame.is_strike or prev_frame.is_spare):
            self._add_score_for_last_frame(prev_frame, score)
           
        # the ordinary second shot 
        else:
            if prev_frame.score_one + score > MAX_SCORE:
                raise InvalidScoreException()

            self._add_score_for_second_ball(prev_frame, score)

    def _is_invalid_score(self, score):
        return score < MIN_SCORE or score > MAX_SCORE or not isinstance(score, (int, long))

    # create a new frame
    # check if it's the last frame and if there is a strike
    # and add the score
    def _create_new_frame(self, score):
        Frame.objects.create(
            game=self,
            score_one=score,
            is_strike=self._is_strike(score),
            is_last_frame=self._adding_last_frame()
        )

    # last frame and there was a strike or spare
    # if it's round three add and close the game
    # otherwise leave the game open
    def _add_score_for_last_frame(self, frame, score):
        if frame.score_two is None:
            frame.score_two = score
            frame.save()
        else:
            frame.score_three = score
            frame.save()
            self.is_over = True
            self.save()

    # check if it is a spare and if it's the last frame 
    # and it's not a spare the game is over
    def _add_score_for_second_ball(self, frame, score):
        frame.score_two = score
        frame.is_spare = self._is_spare(frame.score_one, score)
        frame.save()

        if frame.is_last_frame and not frame.is_spare:
            self.is_over = True
            self.save()

    def _adding_last_frame(self):
        return self.frames.count() == MAX_SCORE - 1 
    
    def _is_strike(self, score):
        if score == MAX_SCORE:
            return True
        return False

    def _is_spare(self, score_one, score_two):
        if score_one + score_two == MAX_SCORE:
            return True
        return False

    # calculate the total score and also the score of each frame
    # return score and a list of frames with score attribute per frame
    def calculate_score(self):
        frame_list = [frame for frame in self.frames.all()]
        frame_list_calculated = []

        def _get_next_frame(frame_list, index):
            try:
                next_frame = frame_list[index]
            except IndexError:
                next_frame = None
            return next_frame

        for index, frame in enumerate(frame_list):
            # normal score per frame
            score = frame.get_frame_score()

            next_frame = _get_next_frame(frame_list, index+1)
            # check for extra points because of spare
            if frame.is_spare and next_frame:
                score += next_frame.get_score_one()
            
            # check for extra points because of strike
            elif frame.is_strike and next_frame:
                score += next_frame.get_frame_score_for_strike()

                next_next_frame = _get_next_frame(frame_list, index+2)
                if next_frame.is_strike and next_next_frame:
                    score += next_next_frame.get_score_one()

            frame_list_calculated.append(score)
            frame_list[index].score = sum(frame_list_calculated)
            
        return sum(frame_list_calculated), frame_list



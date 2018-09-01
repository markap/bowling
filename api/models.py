# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class GameOverException(Exception):
    pass

class InvalidScoreException(Exception):
    pass


class Frame(models.Model):
    game = models.ForeignKey('Game', related_name='frames') # more attributes?
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    is_spare = models.BooleanField(default=False)
    is_strike = models.BooleanField(default=False)
    is_last_frame = models.BooleanField(default=False)

    score_one = models.IntegerField(null=True, blank=True)#min max
    score_two = models.IntegerField(null=True, blank=True)#min max
    score_three = models.IntegerField(null=True, blank=True)#min max

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
        return not self.is_last_frame and (self.is_strike or (self.score_one is not None and self.score_two is not None))



class Game(models.Model):
    is_over = models.BooleanField(default=False)

    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def add_score(self, score):
        if self.is_over:
            raise GameOverException()

        if score < 0 or score > 10 or not isinstance(score, (int, long)): # todo function
            raise InvalidScoreException()


        prev_frame = self.frames.last()

        # there is no frame yet 
        # or the previous frame is already closed, 
        # so let's create a new frame
        # check if it's the last frame and if there is a strike
        # and add the score
        if prev_frame is None or (prev_frame and prev_frame.is_closed()): 
            Frame.objects.create(
                game=self,
                score_one=score,
                is_strike=self._is_strike(score),
                is_last_frame=self._adding_last_frame()
            )


        # we playing in the last frame and we have either a spare or a strike
        # if it's round three add and close the game, otherwise leave the game open
        elif prev_frame.is_last_frame and (prev_frame.is_strike or prev_frame.is_spare):
            if prev_frame.score_two is None:
                prev_frame.score_two = score
                prev_frame.save()
            else:
                prev_frame.score_three = score
                prev_frame.save()

                self.is_over = True
                self.save()
            
        # the typical second shot 
        # check if it is a spare and if it's the last frame 
        # and it's not a spare the game is over
        else:
            # update prev frame
            if prev_frame.score_one + score > 10: # function
                raise InvalidScoreException()

            prev_frame.score_two = score
            prev_frame.is_spare = self._is_spare(prev_frame.score_one, score)
            prev_frame.save()

            if prev_frame.is_last_frame and not prev_frame.is_spare:
                self.is_over = True
                self.save()


    def _adding_last_frame(self):
        print self.frames.count()
        return self.frames.count() == 9 # todo const
    
    def _is_strike(self, score):
        if score == 10: #TODO const #todo function
            return True
        return False

    def _is_spare(self, score_one, score_two):
        if score_one + score_two == 10: #TODO const
            return True
        return False


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
            score = frame.get_frame_score()

            next_frame = _get_next_frame(frame_list, index+1)
            if frame.is_spare and next_frame:
                score += next_frame.get_score_one()
            
            elif frame.is_strike and next_frame:
                score += next_frame.get_frame_score_for_strike()

                next_next_frame = _get_next_frame(frame_list, index+2)
                if next_frame.is_strike and next_next_frame:
                    score += next_next_frame.get_score_one()

            frame_list_calculated.append(score)
            frame_list[index].score = sum(frame_list_calculated)
            
        return sum(frame_list_calculated), frame_list


                





        



# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Frame(models.Model):
    game = models.ForeignKey('Game', related_name='frames') # more attributes?
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    is_spare = models.BooleanField(default=False)
    is_strike = models.BooleanField(default=False)

    score_one = models.IntegerField(null=True, blank=True)#min max
    score_two = models.IntegerField(null=True, blank=True)#min max
    score_three = models.IntegerField(null=True, blank=True)#min max

    def get_score_one(self):
        return self.score_one or 0

    def get_frame_score(self):
        return sum([self.score_one or 0,
                    self.score_two or 0,
                    self.score_three or 0])

    def is_closed(self):
        return self.is_strike or (self.score_one and self.score_two)



class Game(models.Model):
    frame_count = models.IntegerField(null=True, blank=True)#min max

    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def add_score(self, score):
        # check if frame is below 10 to create new one
        # check if game is over
        # if last frame and spare or strike, allow more balls

        # check score between 0 and 10
        # value error


        prev_frame = self.frames.last()

        # no prev frame or prev frame closed -> create new frame
        if prev_frame is None or (prev_frame and prev_frame.is_closed()): #and not prev_frame.is_last_frame): #todo improve
            Frame.objects.create(
                game=self,
                score_one=score,
                is_strike=self._is_strike(score),
                #is_last_frame=self._is_last_frame()
            )
        #elif prev_frame.is_last_frame and strike:
        #elif prev_frame.is_last_frame and spare:
            
        else:
            # update prev frame
            prev_frame.score_two = score
            prev_frame.is_spare = self._is_spare(prev_frame.score_one, score)
            prev_frame.save()

            # if last_frame check if is_strike or is_spare 

            #if last_frame.is_last_frame():
            #    self.is_over = True
            #    self.save()


    def _is_last_frame(self):
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

        def get_next_frame(frame_list, index):
            try:
                next_frame = frame_list[index]
            except IndexError:
                next_frame = None
            return next_frame

        for index, frame in enumerate(frame_list):
            score = frame.get_frame_score()

            next_frame = get_next_frame(frame_list, index+1)
            if frame.is_spare and next_frame:
                score += next_frame.get_score_one()
            
            elif frame.is_strike and next_frame:
                score += next_frame.get_frame_score()

                next_next_frame = get_next_frame(frame_list, index+2)
                if next_frame.is_strike and next_next_frame:
                    score += next_next_frame.get_score_one()

            frame_list_calculated.append(score)
            # instead of frame_list, set an attribute in the frame
            
        print frame_list_calculated
        return sum(frame_list_calculated)


                





        



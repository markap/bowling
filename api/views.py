# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from api import models


ERROR_GAME_DOES_NOT_EXIST = "Game does not exist"


class GameResultView(APIView):

    renderer_classes = (JSONRenderer, )

    def post(self, request, format=None):
        try:
            game = models.Game.objects.get(pk=request.data.get('game_id'))
            score, frames = game.calculate_score()

            data = game.as_dict(score)
            data['frames'] = [f.as_dict() for f in frames]
            return Response(data)
        except models.Game.DoesNotExist:
            return Response({'error': ERROR_GAME_DOES_NOT_EXIST})


class CreateGameView(APIView):

    renderer_classes = (JSONRenderer, )

    def post(self, request, format=None):
        game = models.Game.objects.create()
        return Response({'game_id': game.id})


class AddScoreView(APIView):

    renderer_classes = (JSONRenderer, )

    def post(self, request, format=None):
        try:
            game = models.Game.objects.get(pk=request.data.get('game_id'))
            game.add_score(request.data.get('score'))
            return Response()
        except (models.InvalidScoreException, models.GameOverException) as e:
            return Response({'error': e.message})
        except models.Game.DoesNotExist:
            return Response({'error': ERROR_GAME_DOES_NOT_EXIST})


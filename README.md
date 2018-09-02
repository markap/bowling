  
# Bowling  API

Simple API for ten-pin bowling. 
[https://en.wikipedia.org/wiki/Ten-pin_bowling#Scoring](https://en.wikipedia.org/wiki/Ten-pin_bowling)

## Installation
```
  git clone git@github.com:markap/bowling.git
  cd bowling
  virtualenv env
  source env/bin/activate
  pip install -r requirements.txt
  python manage.py migrate
```

## Run tests
```
  python manage.py test
```

## Run server
```
  python manage.py runserver
```

## API Documentation

Little API documentation to create a new game, add score and see the current result.
All communication is done in JSON(application/json).

`/api/new/`

Create a new game
 - *method*: *POST*
 - *arguments*: None
 - *success return*:
    - *code*: 200
    - *content*: `{'game_id': 12}`
 - *error return*:
    - *code*: 200
    - *content*: `{'error': "some error message"}`
 
 `/api/add/`

Add score to a game
 - *method*: *POST*
 - *arguments*: `{'game_id': 12, 'score': 5}`
 - *success return*:
    - *code*: 200
    - *content*: None
 - *error return*:
    - *code*: 200
    - *content*: `{'error': "some error message"}`
    
 `/api/result/`

Get result of a game

 - *method*: *POST* (method could be changed to GET for a better REST feeling)
 - *arguments*: `{'game_id': 12}`
 - *success return*:
    - *code*: 200
    - *content*: 
        ```
          {
            "frames": [
                {
                    "frame_id": 8,
                    "score": 20,
                    "score_two": 5,
                    "is_spare": true,
                    "is_last_frame": false,
                    "is_strike": false,
                    "score_one": 5,
                    "score_three": null
                },
                {
                    "frame_id": 9,
                    "score": 30,
                    "score_two": null,
                    "is_spare": false,
                    "is_last_frame": false,
                    "is_strike": true,
                    "score_one": 10,
                    "score_three": null
                }
            ],
            "game_id": 11,
            "is_over": false,
            "score": 30
        }
        ```
 - *error return*:
    - *code*: 200
    - *content*: `{'error': "some error message"}`
 

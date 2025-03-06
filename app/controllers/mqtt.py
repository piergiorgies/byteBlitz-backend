import json
import random
from datetime import datetime
from sqlalchemy.orm import Session

from app.connections.mqtt import MQTTClient
from app.database import get_session
from app.controllers.contest import get_scoreboard
from app.schemas.mqtt import Row, ScoreboardDTO, NotificationDTO


def notification(mqtt_client: MQTTClient, contest_id: int, message: str):
    session_generator = get_session()
    session: Session = next(session_generator)

    # Ottieni l'ora corrente nel formato HH:MM
    current_time = datetime.now().strftime("%H:%M")
    
    # Crea il dizionario con il formato desiderato
    notification_data = {'n': message, 't': current_time}
    
    # Converti il dizionario in JSON
    dto_json = json.dumps(notification_data)
    
    print(dto_json)
    mqtt_client.publish("notificaBerna", dto_json)

def scoreboard(mqtt_client: MQTTClient, contest_id: int):
    session_generator = get_session()
    session: Session = next(session_generator)

    contest_scoreboard = get_scoreboard(contest_id, session)
    # Transform ContestScoreboardDTO to ScoreboardDTO
    rows = []
    for i, userteam in enumerate(contest_scoreboard.userteams):
        total_score = sum(contest_scoreboard.scores[i])
        rows.append(Row(n=userteam, p=total_score))

    # Sort rows by total score in descending order
    rows.sort(key=lambda row: row.p, reverse=True)

    scoreboard_dto = ScoreboardDTO(classifica=rows)
    

    # Convert to JSON
    dto_json = json.dumps(scoreboard_dto.model_dump())

    print(dto_json)
    
    mqtt_client.publish("classificaBerna", dto_json)
    #print("Published message")


    #string = """
    #{
    #   "classifica": [
    #        { "n": "stef", "p": 100 },
    #        { "n": "cazzo", "p": 90 },
    #        { "n": "palle", "p": 80 },
    #        { "n": "caca", "p": 70 },
    #        { "n": "a b c", "p": 70 },
    #        { "n": "supercalifragilistichespiralitoso", "p": 60 },
    #        { "n": "cecio", "p": 50 },
    #        { "n": "tetano", "p": 30 },
    #        { "n": "pene", "p": 20 },
    #        { "n": "blu", "p": 10 }
    #    ]
    #}
    #"""
    #dto = json.loads(string)#

    #random.shuffle(dto['classifica'])

    # Change scores to make it ordered
    #for i, entry in enumerate(dto['classifica']):
    #    entry['p'] = 100 - i * 10
    
    #print(json.dumps(dto))
    
    #mqtt_client.publish("classificaBerna", json.dumps(dto))
    #print("Published message")
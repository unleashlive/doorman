import os, sys
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "vendored"))

from boto3 import client
import boto3
import io
import logging
import json
from contextlib import closing
from pydub import AudioSegment
from pydub.playback import play

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def speak(text):
    client = boto3.client('polly', region_name='us-east-1')
    response = client.synthesize_speech(
        OutputFormat='mp3',
        Text=text,
        TextType='text',
        VoiceId='Brian'
    )

    print(response)

    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            try:
                data = stream.read()
                song = AudioSegment.from_file(io.BytesIO(data), format="mp3")
                play(song)
            except IOError as error:
                print(error)
                sys.exit(-1)


def playAudioFile(path):
    data = open(os.path.realpath(path), 'rb').read()
    song = AudioSegment.from_file(io.BytesIO(data), format="mp3")
    play(song)


def function_handler(event, context):
    print(event)
    speak("Hello " + event["name"])
    if "emotion" in event: 
        speak("You look " + event["emotion"])

sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='doorman-guidepost')
while True:
    for message in queue.receive_messages():
        print(message.body)
        body = json.loads(message.body)
        function_handler(json.loads(body["Message"]), None)
        message.delete()

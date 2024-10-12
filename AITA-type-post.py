import os
import random
from moviepy.editor import *
import boto3
from my_secrets.AWScreds import aws_access_key, aws_secret_access_key
import re
import addTextToImage as imager

narrationGender = "male"
AWSLimit = 3000
textArray = []
textTitle = ""
subreddit = ""
username = ""
counter = 1

os.system('clear')
os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key
os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_access_key
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

def getPost():
    global textTitle
    global subreddit
    global username
    with open("resources/AITAPostText.txt") as textFile:
        textTitle = textFile.readline().strip()
        textBody = textFile.read().replace("\n", " ").replace("\r", " ").strip()

    # Split the post's text into 3000 or less char chunks for AWS free tier 😎
    while True:
        if (len(textBody) < AWSLimit):
            break

        textBlock = textBody[0:AWSLimit]
        nearestSpace = textBlock.rfind(". ", 0, AWSLimit)

        textBeforeFullstop = textBody[0:nearestSpace+2].strip() # +2 to account for the actual ". "
        textArray.append(textBeforeFullstop)
        textBody = textBody[nearestSpace+2:]
    textArray.append(textBody.strip())

    betweenBracketsPattern = r"\{([^}]+)\}"
    textInBrackets = re.search(betweenBracketsPattern, textTitle).group(1)
    subreddit, username = textInBrackets.split(',')
    textTitle = textTitle[:textTitle.rfind('{')].strip()
    print("Subreddit: "+subreddit+" Username: "+username+" Post Title: "+textTitle)
    print("Post Text: ")
    for block in textArray:
        print("BLOCK: "+block)


def getTTS():
    global counter
    client = boto3.client("polly")
    print(boto3.Session().get_credentials())
    # TTS Reading Title
    if (narrationGender == "male"):
        response = client.synthesize_speech(
            Text=textTitle,
            OutputFormat="mp3",
            VoiceId="Matthew",
            Engine="neural"
    )
    if (narrationGender == "female"):
        response = client.synthesize_speech(
            Text=textTitle,
            OutputFormat="mp3",
            VoiceId="Joanna",
            Engine="neural"
    )
    audioPath = f'tts/titleTTS.mp3'
    with open(audioPath, 'wb') as file:
        file.write(response['AudioStream'].read())
    print("AWS Wrote TitleTTS to "+audioPath+".")

    for block in textArray:
        if (narrationGender == "male"):
            response = client.synthesize_speech(
                Text=block,
                OutputFormat="mp3",
                VoiceId="Matthew",
                Engine="neural")
        if (narrationGender == "female"):
            response = client.synthesize_speech(
                Text=block,
                OutputFormat="mp3",
                VoiceId="Joanna",
                Engine="neural"
        )
        audioPath = f'tts/bodytextTTS{counter}.mp3'
        with open(audioPath, 'wb') as file:
            file.write(response['AudioStream'].read())
        print(f'AWS Wrote bodyTTS{counter} to '+audioPath+'.')
        counter += 1


def composeVideo():
    global counter
    finalAudioArray = []
    finalAudioArray.append(AudioFileClip("tts/titleTTS.mp3"))
    finalAudioArray.append(AudioFileClip("resources/silence.mp3"))

    for x in range(counter-1):
        audioBodytextClip = AudioFileClip(f"tts/bodytextTTS{x+1}.mp3")
        finalAudioArray.append(audioBodytextClip)
    print(finalAudioArray)
    finalAudio = concatenate_audioclips(finalAudioArray)

    # Make the intro image #
    imager.addTextToTemplate(username, textTitle)
    imagePath = "introImage.png"
    image = ImageClip(imagePath)
    image = image.set_duration(AudioFileClip("tts/titleTTS.mp3").duration+1).set_position("center")

    fullVideo = VideoFileClip("resources/MCParkour1.mp4")
    randomStartpoint = random.randint(0,int(fullVideo.duration)-int(finalAudio.duration)+10)
    clip = fullVideo.subclip(randomStartpoint, randomStartpoint+finalAudio.duration)

    videoWithAudio = clip.set_audio(finalAudio)
    finalVideo = CompositeVideoClip([videoWithAudio, image])
    finalVideo.write_videofile("finalVideo.mp4")


getPost()
getTTS()
composeVideo()
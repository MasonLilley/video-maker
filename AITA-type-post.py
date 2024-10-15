import os
import random
from moviepy.editor import *
import boto3
from my_secrets.AWScreds import aws_access_key, aws_secret_access_key
import re
import addTextToImage as imager
from pydub import AudioSegment

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
    # Using pydub for the audio b/c moviepy had some weird audio artifacts
    finalAudioArray = ["tts/titleTTS.mp3", "resources/silence.mp3"]
    # Moviepy to find length of audio clip because we need the title's length for the intro image
    titleTTSLength = AudioFileClip("tts/titleTTS.mp3").duration

    for x in range(counter-1):
        print(f"Appending bodytextTTS{x+1}.mp3!")
        audioBodytextClip = f"tts/bodytextTTS{x+1}.mp3"
        finalAudioArray.append(audioBodytextClip)

    combinedAudio = AudioSegment.from_file(finalAudioArray[0])
    for file in finalAudioArray[1:]:
        next_segment = AudioSegment.from_file(file)
        combinedAudio += next_segment
    combinedAudio.export("tts/FinalTTS.mp3", format="mp3")

    # Make the intro image #
    imager.addTextToTemplate(username, textTitle)
    imagePath = "introImage.png"
    image = ImageClip(imagePath)
    image = image.set_duration(titleTTSLength+1).set_position("center")

    finalAudio = AudioFileClip("tts/FinalTTS.mp3")
    fullVideo = VideoFileClip("resources/MCParkour3HDVertical.mp4")
    randomStartpoint = random.randint(0,int(fullVideo.duration)-int(finalAudio.duration)+10)
    clip = fullVideo.subclip(randomStartpoint, randomStartpoint+finalAudio.duration)

    #fast render:
    # clip = fullVideo.subclip(randomStartpoint, randomStartpoint+10)

    videoWithAudio = clip.set_audio(finalAudio)
    finalVideo = CompositeVideoClip([videoWithAudio, image])


    finalVideo.write_videofile("finalVideo.mp4")



getPost()
getTTS()
composeVideo()
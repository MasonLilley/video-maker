import os
import random
from moviepy.editor import *
import boto3
from my_secrets.AWScreds import aws_access_key, aws_secret_access_key
import re
import addTextToImage as imager

narrationGender = "male"
AWSLimit = 3000
comments = []
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
    global comments
    with open("resources/BrainrotPostText.txt") as textFile:
        textTitle = textFile.readline().strip()
        betweenBracketsPattern = r"\{([^}]+)\}"
        textInBrackets = re.search(betweenBracketsPattern, textTitle).group(1)
        subreddit, username = textInBrackets.split(',')
        textTitle = textTitle[:textTitle.rfind('{')].strip()
        content = textFile.read()
    comments = [entry.strip() for entry in content.split('---') if entry.strip()]




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
    audioPath = f'tts/brainrotTitleTTS.mp3'
    with open(audioPath, 'wb') as file:
        file.write(response['AudioStream'].read())
    print("AWS Wrote TitleTTS to "+audioPath+".")

    #TTS Reading Comments
    for comment in comments:
        if (narrationGender == "male"):
            response = client.synthesize_speech(
                Text=comment,
                OutputFormat="mp3",
                VoiceId="Matthew",
                Engine="neural"
            )
        if (narrationGender == "female"):
            response = client.synthesize_speech(
                Text=comment,
                OutputFormat="mp3",
                VoiceId="Joanna",
                Engine="neural"
            )
        audioPath = f'tts/brainrotCommentTTS{counter}.mp3'
        with open(audioPath, 'wb') as file:
            file.write(response['AudioStream'].read())
        print("AWS Wrote TitleTTS to "+audioPath+".")
        counter += 1


def composeVideo():
    global counter
    finalAudioArray = []
    wooshSound = AudioFileClip("resources/sounds/woosh.mp3")
    dingSound = AudioFileClip("resources/sounds/ding.mp3").set_start(0.2)
    titleTTS = AudioFileClip("tts/brainrotTitleTTS.mp3")
    originalImage = ImageClip("introImage.png").set_duration(AudioFileClip("tts/brainrotTitleTTS.mp3").duration).set_position("center")
    bgVideo = VideoFileClip("resources/SubwaySurfers1.mp4")

    introAudio = CompositeAudioClip([titleTTS, wooshSound, dingSound])

    finalAudioArray.append(introAudio)
    finalAudioArray.append(AudioFileClip("resources/silence.mp3"))
    for x in range(counter - 1):
        audioBodytextClip = AudioFileClip(f"tts/brainrotCommentTTS{x + 1}.mp3")
        finalAudioArray.append(audioBodytextClip)
    print(finalAudioArray)
    finalAudio = concatenate_audioclips(finalAudioArray)

    imager.addTextToTemplate(username, textTitle)

    # Scale image function: start at 3x and decrease to 1x over 0.2 seconds
    def scale_image(t):
        if t < 0.2:
            return 3 - (2 * (t / 0.2))  # Scale from 3 to 1
        else:
            return 1

    animatedImage = originalImage.set_duration(0.2).resize(scale_image).set_position("center")  
    # ^ Remember to set duration to match scaling time ^

    randomStartpoint = random.randint(60, int(bgVideo.duration) - int(finalAudio.duration) + 10)
    clip = bgVideo.subclip(randomStartpoint, randomStartpoint + finalAudio.duration)

    # Remove in production
    # clip = bgVideo.subclip(randomStartpoint, randomStartpoint + 10)

    videoWithAudio = clip.set_audio(finalAudio)
    finalVideo = CompositeVideoClip([videoWithAudio, originalImage, animatedImage])
    finalVideo.write_videofile("finalVideo.mp4")





getPost()
print(comments)
getTTS()
composeVideo()
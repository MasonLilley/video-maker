from aeneas.executetask import ExecuteTask
from aeneas.task import Task
from pydub import AudioSegment

# Check and ensure the WAV file is 16-bit PCM, mono
audio_path = "finalTTSforcaptions.wav"
sound = AudioSegment.from_wav(audio_path)

if sound.channels != 1 or sound.sample_width != 2:
    print("Converting audio to 16-bit PCM, mono...")
    sound = sound.set_channels(1).set_sample_width(2)
    audio_path = "converted_audio.wav"
    sound.export(audio_path, format="wav")
    print("Conversion complete.")

# Define the path to your text file
text_path = "resources/rawPostTextForCaptions.txt"
output_srt_path = "output.srt"

# Create an Aeneas Task object with the correct configuration
config_string = "task_language=eng|os_task_file_format=srt|is_text_type=plain"
task = Task(config_string=config_string)
task.audio_file_path_absolute = audio_path
task.text_file_path_absolute = text_path
task.sync_map_file_path_absolute = output_srt_path

# Execute the task using ExecuteTask in version 1.5.0.0
try:
    execute_task = ExecuteTask(task).execute()
    task.output_sync_map_file()
    print(f"SRT captions saved to {output_srt_path}")
except Exception as e:
    print(f"Error during task execution: {e}")

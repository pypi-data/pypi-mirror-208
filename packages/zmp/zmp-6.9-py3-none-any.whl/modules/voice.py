import azure.cognitiveservices.speech as speechsdk
import logging as log

log.info('Configuring Azure speech engine')
speech_config = speechsdk.SpeechConfig(subscription="f0e19b6310134d73a156d1a8aad04b73", region="westus")
speech_config.speech_synthesis_voice_name = "en-US-JaneNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
log.info('Azure speech engine configured')

def speak(text: str):
    log.info(f'Generating speech from text:\n{text}')
    result = speech_synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        if cancellation_details.reason == speechsdk.CancellationReason.Error: raise Exception(f"Speech synthesis canceled: {cancellation_details.reason}\nError details: {cancellation_details.error_details}")
        raise Exception(f"Speech synthesis canceled: {cancellation_details.reason}")
    return text
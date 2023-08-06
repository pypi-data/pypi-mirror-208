'''
  For more samples please visit https://github.com/Azure-Samples/cognitive-services-speech-sdk 
'''

import azure.cognitiveservices.speech as speechsdk

# Creates an instance of a speech config with specified subscription key and service region.
speech_key = "817cb92bec4c4e6ba8d5f6eb5e77ea88"
service_region = "germanywestcentral"

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# Note: the voice setting will not overwrite the voice element in input SSML.
speech_config.speech_synthesis_voice_name = "nl-NL-ColetteNeural"

text = (
    "Eén van uw medewerkers is arbeidsongeschikt. "
    "Het betreft de heer I. Roe-hoeless-in, dat volgens het Nederlands "
    "telefoonalfabet als volgt wordt gespeld: Rudolf, Utrecht, Hendrik, "
    "Utrecht, Lodewijk, Eduard, Simon, Simon, Isaak, Nico. De medewerker "
    "is arbeidsongeschikt sedert 1 april 2024 en het verplegingsadres "
    "is het adres dat bij uw administratie bekend is ten aanzien van "
    "deze medewerker. De medewerker weet niet tot wanneer de "
    "arbeidsongeschiktheid voortduurt. "
    "De arbeidsongeschiktheid is niet het gevolg van een bedrijfsongeval. "
)

#text = (
#    "Eén van uw medewerkers is arbeidsongeschikt. "
#    "Deze medewerker is via u werkzaam bij Wehkamp, te Zwolle. "
#    "Het betreft de heer C.Y. Ruhulessin, dat volgens het Nederlands "
#    "telefoonalfabet als volgt wordt gespeld: Rudolf, Utrecht, Hendrik, "
#    "Utrecht, Lodewijk, Eduard, Simon, Simon, Isaak, Nico. De medewerker "
#    "is arbeidsongeschikt sedert 1 april 2024 en het verplegingsadres "
#    "is de Keppelstraat 9, te Zutphen. "
#    "De medewerker weet niet tot wanneer de arbeidsongeschiktheid voortduurt. "
#    "Voor de volledigheid is deze kennisgeving ook verzonden naar het emailadres zwolle.wehkamp@timing.nl. "
#)
text = text + f"Herhaling: {text}"
text = f"Goedendag. {text}"
text = f"{text} Einde bericht."

# use the default speaker as audio output.
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

result = speech_synthesizer.speak_text_async(text).get()
# Check result
if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized for text [{}]".format(text))
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))



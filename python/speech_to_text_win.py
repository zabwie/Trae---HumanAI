import json
import sys
import subprocess
import tempfile
import os
import time

class SpeechToText:
    def __init__(self):
        pass
    
    def start_listening(self):
        try:
            # Create a temporary VBS script with a different approach
            vbs_content = '''
            ' Create the speech recognition engine
            Dim SpeechRecognizer
            Set SpeechRecognizer = CreateObject("SAPI.SpSharedRecognizer")
            
            ' Create a recognition context
            Dim RecognitionContext
            Set RecognitionContext = SpeechRecognizer.CreateRecoContext
            
            ' Create and load dictation grammar
            Dim Grammar
            Set Grammar = RecognitionContext.CreateGrammar(0)
            Grammar.DictationLoad "", 0
            
            ' Activate the grammar
            Grammar.DictationSetState 1
            
            ' Create a file to write results
            Dim FSO, OutputFile
            Set FSO = CreateObject("Scripting.FileSystemObject")
            Set OutputFile = FSO.CreateTextFile("speech_result.txt", True)
            
            ' Speak prompt
            Dim Voice
            Set Voice = CreateObject("SAPI.SpVoice")
            Voice.Speak "Please speak now"
            
            ' Set up event handler for recognition
            RecognitionContext.RetainedAudio = 5
            
            ' Show message box to wait for user to speak
            MsgBox "Speak now. Click OK when done speaking."
            
            ' Get the audio input
            Dim RecoResult
            Set RecoResult = RecognitionContext.CreateResult
            
            ' Try to get the recognized text
            Dim Phrase
            On Error Resume Next
            Set Phrase = RecoResult.PhraseInfo
            If Not Phrase Is Nothing Then
                OutputFile.WriteLine Phrase.GetText
            End If
            
            ' Clean up
            OutputFile.Close
            '''
            
            # Write the VBS script to a temporary file
            fd, vbs_path = tempfile.mkstemp(suffix='.vbs')
            with os.fdopen(fd, 'w') as f:
                f.write(vbs_content)
            
            # Create a file to store the speech text
            speech_file = os.path.join(os.path.dirname(vbs_path), "speech_result.txt")
            
            # Run the VBS script
            print("Listening... (a dialog will appear)")
            subprocess.call(['cscript', vbs_path])
            
            # Wait a moment for the file to be written
            time.sleep(1)
            
            # Read the speech text
            text = ""
            if os.path.exists(speech_file):
                with open(speech_file, 'r') as f:
                    text = f.read().strip()
                # Clean up
                os.remove(speech_file)
            
            # Clean up VBS script
            os.remove(vbs_path)
            
            return text
        except Exception as e:
            print(f"Error in speech recognition: {str(e)}")
            return ""

if __name__ == "__main__":
    # This will be used when called directly from Node.js
    stt = SpeechToText()
    result = stt.start_listening()
    print(json.dumps({"text": result}))
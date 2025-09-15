import React, { useState, useRef } from 'react';
import { Box, Button, Typography, LinearProgress } from '@mui/material';
import { Mic, MicOff, Stop, Send } from '@mui/icons-material';

function AudioRecorder({ onAudioRecorded, disabled = false }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [hasRecording, setHasRecording] = useState(false);
  
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      chunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };
      
      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setHasRecording(true);
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
        
        // Call the callback with the audio blob
        if (onAudioRecorded) {
          onAudioRecorded(audioBlob);
        }
      };
      
      mediaRecorderRef.current.start(1000); // Collect data every second
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Please allow microphone access to record your answer');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const resetRecording = () => {
    setHasRecording(false);
    setRecordingTime(0);
  };

  return (
    <Box sx={{ 
      p: 2, 
      border: '2px dashed', 
      borderColor: isRecording ? 'primary.main' : 'grey.300',
      borderRadius: 2,
      textAlign: 'center',
      bgcolor: isRecording ? 'primary.50' : 'transparent'
    }}>
      <Typography variant="h6" gutterBottom>
        Record Your Answer
      </Typography>
      
      {isRecording && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body1" color="primary" gutterBottom>
            Recording... {formatTime(recordingTime)}
          </Typography>
          <LinearProgress 
            variant="determinate" 
            value={(recordingTime % 60) / 60 * 100} 
            sx={{ height: 6, borderRadius: 3 }}
          />
        </Box>
      )}
      
      {hasRecording && !isRecording && (
        <Typography variant="body1" color="success.main" gutterBottom>
          Answer recorded ({formatTime(recordingTime)}) and submitted!
        </Typography>
      )}
      
      <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
        {!isRecording && !hasRecording && (
          <Button
            variant="contained"
            startIcon={<Mic />}
            onClick={startRecording}
            disabled={disabled}
            size="large"
          >
            Start Recording
          </Button>
        )}
        
        {isRecording && (
          <Button
            variant="contained"
            color="error"
            startIcon={<Stop />}
            onClick={stopRecording}
            size="large"
          >
            Stop & Submit
          </Button>
        )}
        
        {hasRecording && !isRecording && (
          <Button
            variant="outlined"
            startIcon={<Mic />}
            onClick={resetRecording}
            size="large"
          >
            Record Again
          </Button>
        )}
      </Box>
      
      <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
        {isRecording ? 
          'Speak clearly into your microphone. Click "Stop & Submit" when finished.' :
          'Click the microphone button to start recording your answer.'
        }
      </Typography>
    </Box>
  );
}

export default AudioRecorder;
import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip
} from '@mui/material';
import { Mic, MicOff, Videocam, VideocamOff, PlayArrow, Code } from '@mui/icons-material';
import axios from 'axios';
import * as faceapi from 'face-api.js';
import ProctorMonitor from '../components/ProctorMonitor';
import AudioRecorder from '../components/AudioRecorder';

const API_BASE_URL = 'http://localhost:8000';

function InterviewPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [videoEnabled, setVideoEnabled] = useState(true);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [consentDialog, setConsentDialog] = useState(true);
  const [proctorAlerts, setProctorAlerts] = useState([]);
  const [sessionStarted, setSessionStarted] = useState(false);
  
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  // Load questions when component mounts
  useEffect(() => {
    loadQuestions();
  }, [sessionId]);

  const loadQuestions = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/session/${sessionId}/questions`);
      setQuestions(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load interview questions');
      setLoading(false);
    }
  };

  const startMediaCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });
      
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      // Load face-api models for proctoring
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
        faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
        faceapi.nets.faceRecognitionNet.loadFromUri('/models')
      ]);
      
      setSessionStarted(true);
      
    } catch (err) {
      setError('Camera and microphone access required for interview');
    }
  };

  const stopMediaCapture = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
  };

  const toggleVideo = () => {
    if (streamRef.current) {
      const videoTrack = streamRef.current.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setVideoEnabled(videoTrack.enabled);
      }
    }
  };

  const toggleAudio = () => {
    if (streamRef.current) {
      const audioTrack = streamRef.current.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setAudioEnabled(audioTrack.enabled);
      }
    }
  };

  const handleConsent = () => {
    setConsentDialog(false);
    startMediaCapture();
  };

  const nextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      // Interview complete, navigate to coding phase
      navigate(`/coding/${sessionId}/start`);
    }
  };

  const previousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleAudioRecorded = async (audioBlob) => {
    if (!questions[currentQuestionIndex]) return;
    
    const formData = new FormData();
    formData.append('file', audioBlob, 'answer.webm');
    
    try {
      await axios.post(
        `${API_BASE_URL}/session/${sessionId}/audio?question_id=${questions[currentQuestionIndex].id}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      // Auto-advance to next question after successful upload
      setTimeout(() => {
        nextQuestion();
      }, 1000);
      
    } catch (err) {
      setError('Failed to upload audio answer');
    }
  };

  const handleProctorAlert = (alert) => {
    setProctorAlerts(prev => [...prev.slice(-4), alert]); // Keep last 5 alerts
  };

  const currentQuestion = questions[currentQuestionIndex];
  const progress = questions.length > 0 ? ((currentQuestionIndex + 1) / questions.length) * 100 : 0;

  if (loading) {
    return (
      <Container>
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <LinearProgress />
          <Typography sx={{ mt: 2 }}>Loading interview questions...</Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Alert severity="error" sx={{ mt: 4 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 2, mb: 4 }}>
      {/* Consent Dialog */}
      <Dialog open={consentDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Interview Consent</DialogTitle>
        <DialogContent>
          <Typography paragraph>
            This AI-powered interview will record your audio and video for evaluation purposes. 
            The system will monitor for potential integrity issues during the interview.
          </Typography>
          <Typography paragraph>
            By proceeding, you consent to:
          </Typography>
          <ul>
            <li>Audio recording of your responses</li>
            <li>Video recording for proctoring purposes</li>
            <li>Face detection and monitoring</li>
            <li>Tab switching and activity monitoring</li>
          </ul>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => navigate('/')}>Decline</Button>
          <Button variant="contained" onClick={handleConsent}>
            I Consent & Start Interview
          </Button>
        </DialogActions>
      </Dialog>

      {sessionStarted && (
        <Box sx={{ display: 'flex', gap: 2, height: 'calc(100vh - 100px)' }}>
          {/* Main Interview Area */}
          <Paper sx={{ flex: 1, p: 3, display: 'flex', flexDirection: 'column' }}>
            {/* Progress */}
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="h6">
                  Question {currentQuestionIndex + 1} of {questions.length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {Math.round(progress)}% Complete
                </Typography>
              </Box>
              <LinearProgress variant="determinate" value={progress} />
            </Box>

            {/* Current Question */}
            {currentQuestion && (
              <Card variant="outlined" sx={{ mb: 3, flex: 1 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                    <Chip 
                      label={currentQuestion.question_type} 
                      color="primary" 
                      size="small" 
                    />
                    <Chip 
                      label={currentQuestion.difficulty || 'medium'} 
                      size="small" 
                    />
                  </Box>
                  
                  <Typography variant="h5" component="h2" gutterBottom>
                    {currentQuestion.question_text}
                  </Typography>
                  
                  {currentQuestion.expected_skills && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Skills being evaluated:
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {currentQuestion.expected_skills.map((skill, index) => (
                          <Chip 
                            key={index} 
                            label={skill} 
                            size="small" 
                            variant="outlined" 
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Audio Recorder */}
            <Box sx={{ mt: 'auto' }}>
              <AudioRecorder
                onAudioRecorded={handleAudioRecorded}
                disabled={!sessionStarted}
              />
            </Box>

            {/* Navigation */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
              <Button 
                onClick={previousQuestion}
                disabled={currentQuestionIndex === 0}
              >
                Previous
              </Button>
              
              <Button
                variant="contained"
                onClick={nextQuestion}
                startIcon={currentQuestionIndex === questions.length - 1 ? <Code /> : <PlayArrow />}
              >
                {currentQuestionIndex === questions.length - 1 ? 'Start Coding' : 'Next Question'}
              </Button>
            </Box>
          </Paper>

          {/* Sidebar - Video and Proctoring */}
          <Paper sx={{ width: 300, p: 2, display: 'flex', flexDirection: 'column' }}>
            {/* Video Feed */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="h6" gutterBottom>
                Video Feed
              </Typography>
              
              <Box sx={{ position: 'relative', mb: 2 }}>
                <video
                  ref={videoRef}
                  autoPlay
                  muted
                  style={{
                    width: '100%',
                    height: '200px',
                    objectFit: 'cover',
                    borderRadius: '8px',
                    backgroundColor: '#000'
                  }}
                />
                
                {/* Video Controls */}
                <Box sx={{ 
                  position: 'absolute', 
                  bottom: 8, 
                  right: 8,
                  display: 'flex',
                  gap: 1
                }}>
                  <Button
                    size="small"
                    variant="contained"
                    color={audioEnabled ? 'primary' : 'error'}
                    onClick={toggleAudio}
                  >
                    {audioEnabled ? <Mic /> : <MicOff />}
                  </Button>
                  
                  <Button
                    size="small"
                    variant="contained"
                    color={videoEnabled ? 'primary' : 'error'}
                    onClick={toggleVideo}
                  >
                    {videoEnabled ? <Videocam /> : <VideocamOff />}
                  </Button>
                </Box>
              </Box>
            </Box>

            {/* Proctoring Monitor */}
            <ProctorMonitor
              videoRef={videoRef}
              sessionId={sessionId}
              onAlert={handleProctorAlert}
            />

            {/* Recent Alerts */}
            {proctorAlerts.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Recent Alerts
                </Typography>
                
                {proctorAlerts.slice(-3).map((alert, index) => (
                  <Alert 
                    key={index} 
                    severity={alert.severity === 'high' ? 'error' : 'warning'}
                    sx={{ mb: 1, fontSize: '0.75rem' }}
                  >
                    {alert.message}
                  </Alert>
                ))}
              </Box>
            )}
          </Paper>
        </Box>
      )}
    </Container>
  );
}

export default InterviewPage;
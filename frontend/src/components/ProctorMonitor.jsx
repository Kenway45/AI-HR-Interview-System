import React, { useEffect, useRef, useState } from 'react';
import { Box, Typography, Alert, Chip } from '@mui/material';
import * as faceapi from 'face-api.js';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function ProctorMonitor({ videoRef, sessionId, onAlert }) {
  const [faceDetectionStatus, setFaceDetectionStatus] = useState('loading');
  const [alerts, setAlerts] = useState([]);
  const [isModelLoaded, setIsModelLoaded] = useState(false);
  
  const intervalRef = useRef(null);
  const lastDetectionRef = useRef(Date.now());
  const alertCooldownRef = useRef({});

  useEffect(() => {
    loadModels();
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (isModelLoaded && videoRef?.current) {
      startFaceDetection();
    }
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isModelLoaded, videoRef]);

  const loadModels = async () => {
    try {
      // Load face-api.js models from public directory
      const MODEL_URL = '/models';
      
      await Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri(MODEL_URL),
        faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL),
        faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL)
      ]);
      
      setIsModelLoaded(true);
      setFaceDetectionStatus('ready');
    } catch (error) {
      console.error('Error loading face detection models:', error);
      setFaceDetectionStatus('error');
    }
  };

  const startFaceDetection = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    intervalRef.current = setInterval(async () => {
      await detectFaces();
    }, 2000); // Check every 2 seconds
  };

  const detectFaces = async () => {
    if (!videoRef?.current || !isModelLoaded) return;
    
    try {
      const detections = await faceapi
        .detectAllFaces(videoRef.current, new faceapi.TinyFaceDetectorOptions())
        .withFaceLandmarks();
      
      const now = Date.now();
      lastDetectionRef.current = now;
      
      if (detections.length === 0) {
        handleAlert('face_not_detected', 'No face detected in camera feed', 'medium');
        setFaceDetectionStatus('no_face');
      } else if (detections.length > 1) {
        handleAlert('multiple_faces', `${detections.length} faces detected - only one person allowed`, 'high');
        setFaceDetectionStatus('multiple_faces');
      } else {
        setFaceDetectionStatus('face_detected');
        
        // Check if person is looking away (simple heuristic based on face landmarks)
        const landmarks = detections[0].landmarks;
        if (landmarks) {
          const nose = landmarks.getNose();
          const leftEye = landmarks.getLeftEye();
          const rightEye = landmarks.getRightEye();
          
          // Simple calculation to detect if person is looking significantly away
          const faceCenter = nose[3]; // Nose tip
          const eyeCenter = {
            x: (leftEye[0].x + rightEye[3].x) / 2,
            y: (leftEye[0].y + rightEye[3].y) / 2
          };
          
          const angle = Math.abs(faceCenter.x - eyeCenter.x);
          if (angle > 30) { // Threshold for looking away
            handleAlert('looking_away', 'Person appears to be looking away from camera', 'low');
          }
        }
      }
      
    } catch (error) {
      console.error('Face detection error:', error);
      setFaceDetectionStatus('error');
    }
  };

  const handleAlert = async (eventType, message, severity) => {
    const now = Date.now();
    const cooldownKey = `${eventType}_${severity}`;
    
    // Implement cooldown to prevent spam
    const lastAlertTime = alertCooldownRef.current[cooldownKey] || 0;
    const cooldownPeriod = severity === 'high' ? 5000 : 15000; // 5s for high, 15s for others
    
    if (now - lastAlertTime < cooldownPeriod) {
      return;
    }
    
    alertCooldownRef.current[cooldownKey] = now;
    
    const alert = {
      eventType,
      message,
      severity,
      timestamp: new Date().toISOString()
    };
    
    // Add to local alerts
    setAlerts(prev => [...prev.slice(-9), alert]); // Keep last 10 alerts
    
    // Call parent callback
    if (onAlert) {
      onAlert(alert);
    }
    
    // Send to backend
    try {
      await axios.post(`${API_BASE_URL}/session/${sessionId}/proctor`, {
        event_type: eventType,
        details: { message, timestamp: alert.timestamp },
        severity: severity
      });
    } catch (error) {
      console.error('Failed to log proctor event:', error);
    }
  };

  const getStatusColor = () => {
    switch (faceDetectionStatus) {
      case 'face_detected':
        return 'success';
      case 'no_face':
        return 'error';
      case 'multiple_faces':
        return 'error';
      case 'loading':
        return 'default';
      case 'ready':
        return 'info';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusText = () => {
    switch (faceDetectionStatus) {
      case 'face_detected':
        return 'Face Detected ✓';
      case 'no_face':
        return 'No Face Detected';
      case 'multiple_faces':
        return 'Multiple Faces';
      case 'loading':
        return 'Loading Models...';
      case 'ready':
        return 'Ready';
      case 'error':
        return 'Detection Error';
      default:
        return 'Unknown Status';
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Proctoring Status
      </Typography>
      
      <Chip 
        label={getStatusText()}
        color={getStatusColor()}
        size="small"
        sx={{ mb: 2 }}
      />
      
      {faceDetectionStatus === 'error' && (
        <Alert severity="warning" sx={{ mb: 2, fontSize: '0.75rem' }}>
          Face detection models failed to load. Proctoring may be limited.
        </Alert>
      )}
      
      {alerts.length > 0 && (
        <Box>
          <Typography variant="subtitle2" gutterBottom>
            Recent Events
          </Typography>
          
          <Box sx={{ maxHeight: '150px', overflow: 'auto' }}>
            {alerts.slice(-3).reverse().map((alert, index) => (
              <Alert 
                key={index}
                severity={alert.severity === 'high' ? 'error' : 'warning'}
                sx={{ mb: 1, fontSize: '0.7rem', py: 0.5 }}
              >
                <Typography variant="caption">
                  {new Date(alert.timestamp).toLocaleTimeString()}: {alert.message}
                </Typography>
              </Alert>
            ))}
          </Box>
        </Box>
      )}
      
      <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 2 }}>
        Monitoring: Face detection, multiple person detection, attention tracking
      </Typography>
    </Box>
  );
}

export default ProctorMonitor;
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Step,
  Stepper,
  StepLabel,
  Card,
  CardContent
} from '@mui/material';
import { CloudUpload, Description, Work } from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const steps = ['Upload Job Description', 'Upload Resume', 'Create Session'];

function HomePage() {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [jdFile, setJdFile] = useState(null);
  const [resumeFile, setResumeFile] = useState(null);
  const [jdSummary, setJdSummary] = useState('');
  const [resumeSummary, setResumeSummary] = useState('');
  const [sessionId, setSessionId] = useState('');

  const handleFileUpload = async (file, type) => {
    setLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(
        `${API_BASE_URL}/upload/${type}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      if (type === 'jd') {
        setJdSummary(response.data.jd_summary);
        setSuccess('Job description processed successfully!');
        setActiveStep(1);
      } else {
        setResumeSummary(response.data.resume_summary);
        setSuccess('Resume processed successfully!');
        setActiveStep(2);
      }
      
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to upload ${type}`);
    } finally {
      setLoading(false);
    }
  };

  const createSession = async () => {
    if (!jdSummary || !resumeSummary) {
      setError('Please upload both job description and resume first');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(
        `${API_BASE_URL}/session/create`,
        null,
        {
          params: {
            jd_summary: jdSummary,
            resume_summary: resumeSummary
          }
        }
      );
      
      const newSessionId = response.data.id;
      setSessionId(newSessionId);
      setSuccess('Interview session created successfully!');
      
      // Navigate to interview page after a short delay
      setTimeout(() => {
        navigate(`/interview/${newSessionId}`);
      }, 2000);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create session');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          AI HR Interview System
        </Typography>
        
        <Typography variant="body1" color="text.secondary" align="center" sx={{ mb: 4 }}>
          Upload a job description and resume to start an AI-powered interview session
        </Typography>

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {/* Job Description Upload */}
          <Card variant={activeStep >= 0 ? "outlined" : "elevation"}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Work color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Job Description</Typography>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<CloudUpload />}
                  disabled={loading}
                >
                  Upload Job Description
                  <input
                    hidden
                    accept=".pdf,.docx,.doc,.txt"
                    type="file"
                    onChange={(e) => {
                      const file = e.target.files[0];
                      if (file) {
                        setJdFile(file);
                        handleFileUpload(file, 'jd');
                      }
                    }}
                  />
                </Button>
                
                {jdFile && (
                  <Typography variant="body2" color="text.secondary">
                    {jdFile.name}
                  </Typography>
                )}
              </Box>
              
              {jdSummary && (
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Job Description Summary"
                  value={jdSummary}
                  variant="outlined"
                  InputProps={{ readOnly: true }}
                  sx={{ mt: 2 }}
                />
              )}
            </CardContent>
          </Card>

          {/* Resume Upload */}
          <Card variant={activeStep >= 1 ? "outlined" : "elevation"}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Description color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Resume</Typography>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Button
                  variant="outlined"
                  component="label"
                  startIcon={<CloudUpload />}
                  disabled={loading || activeStep < 1}
                >
                  Upload Resume
                  <input
                    hidden
                    accept=".pdf,.docx,.doc,.txt"
                    type="file"
                    onChange={(e) => {
                      const file = e.target.files[0];
                      if (file) {
                        setResumeFile(file);
                        handleFileUpload(file, 'resume');
                      }
                    }}
                  />
                </Button>
                
                {resumeFile && (
                  <Typography variant="body2" color="text.secondary">
                    {resumeFile.name}
                  </Typography>
                )}
              </Box>
              
              {resumeSummary && (
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Resume Summary"
                  value={resumeSummary}
                  variant="outlined"
                  InputProps={{ readOnly: true }}
                  sx={{ mt: 2 }}
                />
              )}
            </CardContent>
          </Card>

          {/* Create Session */}
          {activeStep >= 2 && (
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Ready to Start Interview
                </Typography>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Click below to create your interview session and begin the AI-powered interview process.
                </Typography>
                
                <Button
                  variant="contained"
                  size="large"
                  onClick={createSession}
                  disabled={loading || !jdSummary || !resumeSummary}
                  startIcon={loading ? <CircularProgress size={20} /> : null}
                  fullWidth
                >
                  {loading ? 'Creating Session...' : 'Start Interview Session'}
                </Button>
              </CardContent>
            </Card>
          )}
        </Box>

        {sessionId && (
          <Box sx={{ mt: 3, p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
            <Typography variant="body2" color="success.dark">
              Session ID: {sessionId}
            </Typography>
            <Typography variant="body2" color="success.dark">
              Redirecting to interview page...
            </Typography>
          </Box>
        )}
      </Paper>
    </Container>
  );
}

export default HomePage;
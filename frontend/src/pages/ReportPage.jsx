import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  LinearProgress,
  Chip,
  Button,
  Grid,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import { 
  Assessment, 
  CheckCircle, 
  Warning, 
  Code, 
  Mic, 
  Security,
  Download,
  Home
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function ReportPage() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadReport();
  }, [sessionId]);

  const loadReport = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/session/${sessionId}/report`);
      setReport(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load interview report');
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Improvement';
  };

  const calculateOverallGrade = (score) => {
    if (score >= 90) return 'A+';
    if (score >= 85) return 'A';
    if (score >= 80) return 'A-';
    if (score >= 75) return 'B+';
    if (score >= 70) return 'B';
    if (score >= 65) return 'B-';
    if (score >= 60) return 'C+';
    if (score >= 55) return 'C';
    if (score >= 50) return 'C-';
    return 'D';
  };

  if (loading) {
    return (
      <Container>
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <CircularProgress />
          <Typography sx={{ mt: 2 }}>Generating interview report...</Typography>
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

  if (!report) {
    return (
      <Container>
        <Alert severity="info" sx={{ mt: 4 }}>
          No report data available for this session.
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 2, mb: 4 }}>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Assessment color="primary" sx={{ mr: 2, fontSize: 32 }} />
          <Box>
            <Typography variant="h4" component="h1">
              Interview Report
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Session ID: {sessionId}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Completed: {new Date(report.created_at).toLocaleDateString()}
            </Typography>
          </Box>
        </Box>

        {/* Overall Score */}
        <Box sx={{ textAlign: 'center', mt: 3 }}>
          <Typography variant="h2" color={`${getScoreColor(report.overall_score)}.main`}>
            {calculateOverallGrade(report.overall_score)}
          </Typography>
          <Typography variant="h4" color="text.secondary">
            {Math.round(report.overall_score)}% Overall Score
          </Typography>
          <Typography variant="h6" color={`${getScoreColor(report.overall_score)}.main`}>
            {getScoreLabel(report.overall_score)}
          </Typography>
        </Box>
      </Paper>

      <Grid container spacing={3}>
        {/* Interview Answers Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Mic color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Interview Performance</Typography>
              </Box>
              
              {report.answers && report.answers.length > 0 ? (
                <>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" gutterBottom>
                      Average Interview Score
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={report.overall_score}
                      color={getScoreColor(report.overall_score)}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {Math.round(report.overall_score)}% ({report.answers.length} questions answered)
                    </Typography>
                  </Box>

                  <Typography variant="subtitle2" gutterBottom>
                    Question-by-Question Breakdown:
                  </Typography>
                  
                  <List dense>
                    {report.answers.map((answer, index) => (
                      <React.Fragment key={index}>
                        <ListItem sx={{ px: 0 }}>
                          <ListItemText
                            primary={`Question ${index + 1}`}
                            secondary={
                              <Box>
                                <Typography variant="body2" component="span">
                                  Score: {Math.round(answer.score)}%
                                </Typography>
                                {answer.evaluation?.feedback && (
                                  <Typography variant="body2" color="text.secondary">
                                    {answer.evaluation.feedback.substring(0, 100)}...
                                  </Typography>
                                )}
                              </Box>
                            }
                          />
                          <Box sx={{ textAlign: 'right' }}>
                            <Chip
                              label={`${Math.round(answer.score)}%`}
                              color={getScoreColor(answer.score)}
                              size="small"
                            />
                          </Box>
                        </ListItem>
                        {index < report.answers.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                </>
              ) : (
                <Typography color="text.secondary">
                  No interview answers recorded
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Coding Performance Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Code color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Coding Performance</Typography>
              </Box>
              
              {report.coding_tasks && report.coding_tasks.length > 0 ? (
                <>
                  <Typography variant="body2" gutterBottom>
                    Tasks Completed: {report.coding_tasks.length}
                  </Typography>
                  
                  <List dense>
                    {report.coding_tasks.map((task, index) => (
                      <React.Fragment key={index}>
                        <ListItem sx={{ px: 0 }}>
                          <ListItemText
                            primary={task.title}
                            secondary={
                              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                                <Chip label={task.difficulty} size="small" />
                                <Chip 
                                  label="Completed" 
                                  color="success" 
                                  size="small" 
                                />
                              </Box>
                            }
                          />
                        </ListItem>
                        {index < report.coding_tasks.length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                </>
              ) : (
                <Typography color="text.secondary">
                  No coding tasks completed
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Proctoring Summary */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Security color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Integrity Monitoring</Typography>
              </Box>
              
              {report.proctor_summary ? (
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={4}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="text.secondary">
                        {report.proctor_summary.total_events}
                      </Typography>
                      <Typography variant="body2">
                        Total Events
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={4}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography 
                        variant="h4" 
                        color={report.proctor_summary.high_severity_events > 0 ? 'error' : 'success'}
                      >
                        {report.proctor_summary.high_severity_events}
                      </Typography>
                      <Typography variant="body2">
                        High Priority Alerts
                      </Typography>
                    </Box>
                  </Grid>
                  
                  <Grid item xs={12} sm={4}>
                    <Box sx={{ textAlign: 'center' }}>
                      {report.proctor_summary.high_severity_events === 0 ? (
                        <CheckCircle color="success" sx={{ fontSize: 32 }} />
                      ) : (
                        <Warning color="error" sx={{ fontSize: 32 }} />
                      )}
                      <Typography variant="body2">
                        Integrity Status
                      </Typography>
                    </Box>
                  </Grid>
                  
                  {report.proctor_summary.event_types && report.proctor_summary.event_types.length > 0 && (
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" gutterBottom>
                        Event Types Detected:
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {report.proctor_summary.event_types.map((eventType, index) => (
                          <Chip 
                            key={index}
                            label={eventType.replace('_', ' ')}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Grid>
                  )}
                </Grid>
              ) : (
                <Typography color="text.secondary">
                  No integrity monitoring data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Detailed Feedback */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Detailed Feedback
              </Typography>
              
              {report.answers && report.answers.some(a => a.evaluation?.feedback) ? (
                report.answers.map((answer, index) => 
                  answer.evaluation?.feedback && (
                    <Box key={index} sx={{ mb: 2 }}>
                      <Typography variant="subtitle2">
                        Question {index + 1} Feedback:
                      </Typography>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {answer.evaluation.feedback}
                      </Typography>
                      
                      {answer.evaluation.strengths && (
                        <Box sx={{ mb: 1 }}>
                          <Typography variant="caption" color="success.main">
                            Strengths: {answer.evaluation.strengths.join(', ')}
                          </Typography>
                        </Box>
                      )}
                      
                      {answer.evaluation.weaknesses && (
                        <Box sx={{ mb: 1 }}>
                          <Typography variant="caption" color="error.main">
                            Areas for improvement: {answer.evaluation.weaknesses.join(', ')}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  )
                )
              ) : (
                <Typography color="text.secondary">
                  No detailed feedback available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box sx={{ mt: 3, textAlign: 'center' }}>
        <Button
          variant="outlined"
          startIcon={<Download />}
          sx={{ mr: 2 }}
          onClick={() => {
            // In a real implementation, this would generate and download a PDF report
            alert('PDF download feature would be implemented here');
          }}
        >
          Download PDF Report
        </Button>
        
        <Button
          variant="contained"
          startIcon={<Home />}
          onClick={() => navigate('/')}
        >
          Start New Interview
        </Button>
      </Box>
    </Container>
  );
}

export default ReportPage;
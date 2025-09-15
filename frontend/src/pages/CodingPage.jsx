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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  CircularProgress,
  Tab,
  Tabs
} from '@mui/material';
import { PlayArrow, Send, Code, CheckCircle, Error } from '@mui/icons-material';
import Editor from '@monaco-editor/react';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';

const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000';

function CodingPage() {
  const { sessionId, taskId } = useParams();
  const navigate = useNavigate();
  
  const [tasks, setTasks] = useState([]);
  const [currentTaskIndex, setCurrentTaskIndex] = useState(0);
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [output, setOutput] = useState('');
  const [testResults, setTestResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  
  const wsRef = useRef(null);
  const editorRef = useRef(null);

  useEffect(() => {
    loadCodingTasks();
    initializeWebSocket();
    
    // Detect tab switching and paste events
    const handleVisibilityChange = () => {
      if (document.hidden && wsRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'tab_switch',
          timestamp: new Date().toISOString()
        }));
      }
    };
    
    const handlePaste = (e) => {
      const pastedContent = e.clipboardData?.getData('text') || '';
      if (pastedContent.length > 20 && wsRef.current) {
        wsRef.current.send(JSON.stringify({
          type: 'paste_event',
          content: pastedContent,
          timestamp: new Date().toISOString()
        }));
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.addEventListener('paste', handlePaste);
    
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.removeEventListener('paste', handlePaste);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [sessionId, taskId]);

  const loadCodingTasks = async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/session/${sessionId}/start_coding`);
      setTasks(response.data.tasks);
      
      if (response.data.tasks.length > 0) {
        const task = response.data.tasks[0];
        setCode(task.starter_code || '# Your code here\n');
        setLanguage(task.language || 'python');
      }
      
      setLoading(false);
    } catch (err) {
      setError('Failed to load coding tasks');
      setLoading(false);
    }
  };

  const initializeWebSocket = () => {
    const wsUrl = `${WS_BASE_URL}/ws/session/${sessionId}/coding/${taskId || 'start'}`;
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onopen = () => {
      console.log('WebSocket connected');
    };
    
    wsRef.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleWebSocketMessage(message);
    };
    
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected');
    };
  };

  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'run_result':
        setRunning(false);
        if (message.success) {
          setOutput(message.stdout || '');
          if (message.stderr) {
            setOutput(prev => prev + '\nErrors:\n' + message.stderr);
          }
        } else {
          setOutput(`Error: ${message.error}`);
        }
        break;
        
      case 'submit_result':
        setSubmitting(false);
        if (message.success) {
          setTestResults(message);
          setSubmitted(true);
        } else {
          setError(`Submission failed: ${message.error}`);
        }
        break;
        
      case 'proctor_alert':
        // Handle proctoring alerts
        console.warn('Proctor alert:', message.message);
        break;
        
      case 'edit_ack':
        // Code edit acknowledged
        break;
        
      default:
        console.log('Unknown message type:', message.type);
    }
  };

  const handleCodeChange = (value) => {
    setCode(value);
    
    // Send code changes via WebSocket for autosave
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'code_edit',
        code: value,
        cursor: editorRef.current?.getPosition(),
        timestamp: new Date().toISOString()
      }));
    }
  };

  const runCode = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      setError('WebSocket connection not available');
      return;
    }
    
    setRunning(true);
    setOutput('Running...');
    
    wsRef.current.send(JSON.stringify({
      type: 'run_code',
      code: code,
      language: language,
      input: '' // Could add input field for stdin
    }));
  };

  const submitCode = () => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      setError('WebSocket connection not available');
      return;
    }
    
    setSubmitting(true);
    
    wsRef.current.send(JSON.stringify({
      type: 'submit_code',
      code: code,
      language: language
    }));
  };

  const nextTask = () => {
    if (currentTaskIndex < tasks.length - 1) {
      const nextIndex = currentTaskIndex + 1;
      setCurrentTaskIndex(nextIndex);
      const task = tasks[nextIndex];
      setCode(task.starter_code || '# Your code here\n');
      setLanguage(task.language || 'python');
      setOutput('');
      setTestResults(null);
      setSubmitted(false);
    } else {
      // All tasks complete, go to report
      navigate(`/report/${sessionId}`);
    }
  };

  const currentTask = tasks[currentTaskIndex];

  if (loading) {
    return (
      <Container>
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <CircularProgress />
          <Typography sx={{ mt: 2 }}>Loading coding tasks...</Typography>
        </Box>
      </Container>
    );
  }

  if (error && !currentTask) {
    return (
      <Container>
        <Alert severity="error" sx={{ mt: 4 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 2, mb: 4 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: 'flex', gap: 2, height: 'calc(100vh - 150px)' }}>
        {/* Problem Description */}
        <Paper sx={{ width: '40%', p: 2, overflow: 'auto' }}>
          {currentTask && (
            <>
              <Typography variant="h5" gutterBottom>
                {currentTask.title}
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Chip label={currentTask.language} color="primary" size="small" />
                <Chip label={currentTask.difficulty} size="small" />
                <Chip 
                  label={`Task ${currentTaskIndex + 1}/${tasks.length}`} 
                  size="small" 
                />
              </Box>
              
              <Typography variant="body1" paragraph>
                {currentTask.description}
              </Typography>
              
              {/* Test Cases */}
              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                Test Cases
              </Typography>
              
              {currentTask.test_cases?.map((testCase, index) => (
                <Card key={index} variant="outlined" sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="body2" component="div">
                      <strong>Input:</strong>
                      <Box component="pre" sx={{ 
                        bgcolor: 'grey.100', 
                        p: 1, 
                        mt: 1,
                        fontFamily: 'monospace',
                        fontSize: '0.9rem'
                      }}>
                        {testCase.input || 'No input'}
                      </Box>
                    </Typography>
                    
                    <Typography variant="body2" component="div" sx={{ mt: 1 }}>
                      <strong>Expected Output:</strong>
                      <Box component="pre" sx={{ 
                        bgcolor: 'grey.100', 
                        p: 1, 
                        mt: 1,
                        fontFamily: 'monospace',
                        fontSize: '0.9rem'
                      }}>
                        {testCase.expected_output}
                      </Box>
                    </Typography>
                  </CardContent>
                </Card>
              ))}
            </>
          )}
        </Paper>

        {/* Code Editor and Results */}
        <Paper sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {/* Editor */}
          <Box sx={{ flex: 1, minHeight: '400px' }}>
            <Editor
              height="100%"
              language={language}
              value={code}
              onChange={handleCodeChange}
              onMount={(editor) => {
                editorRef.current = editor;
              }}
              options={{
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                fontSize: 14,
                tabSize: 2,
                insertSpaces: true
              }}
            />
          </Box>

          {/* Controls */}
          <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Button
                variant="outlined"
                startIcon={<PlayArrow />}
                onClick={runCode}
                disabled={running || !code.trim()}
              >
                {running ? 'Running...' : 'Run Code'}
              </Button>
              
              <Button
                variant="contained"
                startIcon={<Send />}
                onClick={submitCode}
                disabled={submitting || submitted || !code.trim()}
              >
                {submitting ? 'Submitting...' : 'Submit Solution'}
              </Button>
            </Box>

            {/* Tabs for Output and Test Results */}
            <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
              <Tab label="Output" />
              <Tab label="Test Results" />
            </Tabs>

            <Box sx={{ mt: 2, height: '200px', overflow: 'auto' }}>
              {tabValue === 0 && (
                <Box
                  component="pre"
                  sx={{
                    bgcolor: 'grey.900',
                    color: 'white',
                    p: 2,
                    fontFamily: 'monospace',
                    fontSize: '0.9rem',
                    whiteSpace: 'pre-wrap',
                    minHeight: '100%'
                  }}
                >
                  {output || 'No output yet. Run your code to see results.'}
                </Box>
              )}

              {tabValue === 1 && (
                <Box sx={{ p: 2 }}>
                  {testResults ? (
                    <>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                        {testResults.score === 100 ? (
                          <CheckCircle color="success" sx={{ mr: 1 }} />
                        ) : (
                          <Error color="error" sx={{ mr: 1 }} />
                        )}
                        <Typography variant="h6">
                          Score: {testResults.score}% 
                          ({testResults.passed_tests}/{testResults.total_tests} tests passed)
                        </Typography>
                      </Box>
                      
                      {testResults.test_results?.map((result, index) => (
                        <Card 
                          key={index} 
                          variant="outlined" 
                          sx={{ 
                            mb: 1,
                            borderColor: result.passed ? 'success.main' : 'error.main'
                          }}
                        >
                          <CardContent sx={{ py: 1 }}>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                              {result.passed ? (
                                <CheckCircle color="success" sx={{ fontSize: 16, mr: 1 }} />
                              ) : (
                                <Error color="error" sx={{ fontSize: 16, mr: 1 }} />
                              )}
                              <Typography variant="body2">
                                Test Case {result.test_case}
                              </Typography>
                            </Box>
                            
                            {!result.passed && (
                              <Typography variant="body2" color="text.secondary">
                                Expected: {result.expected}<br />
                                Got: {result.actual}<br />
                                {result.error && `Error: ${result.error}`}
                              </Typography>
                            )}
                          </CardContent>
                        </Card>
                      ))}
                    </>
                  ) : (
                    <Typography color="text.secondary">
                      Submit your solution to see test results
                    </Typography>
                  )}
                </Box>
              )}
            </Box>
          </Box>

          {/* Next Task Button */}
          {submitted && (
            <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
              <Button
                variant="contained"
                fullWidth
                onClick={nextTask}
                startIcon={<Code />}
              >
                {currentTaskIndex < tasks.length - 1 ? 'Next Task' : 'View Report'}
              </Button>
            </Box>
          )}
        </Paper>
      </Box>

      {/* Submission Success Dialog */}
      <Dialog open={submitted && testResults} maxWidth="sm" fullWidth>
        <DialogTitle>
          {testResults?.score === 100 ? 'Perfect Solution!' : 'Solution Submitted'}
        </DialogTitle>
        <DialogContent>
          <Typography>
            You scored {testResults?.score}% on this task 
            ({testResults?.passed_tests}/{testResults?.total_tests} tests passed).
          </Typography>
          {testResults?.score === 100 && (
            <Typography color="success.main" sx={{ mt: 1 }}>
              Excellent work! All test cases passed.
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={nextTask} variant="contained">
            {currentTaskIndex < tasks.length - 1 ? 'Continue to Next Task' : 'View Final Report'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default CodingPage;
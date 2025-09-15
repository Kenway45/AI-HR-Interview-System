import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Box, AppBar, Toolbar, Typography } from '@mui/material';

// Import pages
import HomePage from './pages/HomePage';
import InterviewPage from './pages/InterviewPage';
import CodingPage from './pages/CodingPage';
import ReportPage from './pages/ReportPage';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                🎤 CodeVox
              </Typography>
            </Toolbar>
          </AppBar>
          
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/interview/:sessionId" element={<InterviewPage />} />
            <Route path="/coding/:sessionId/:taskId" element={<CodingPage />} />
            <Route path="/report/:sessionId" element={<ReportPage />} />
          </Routes>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
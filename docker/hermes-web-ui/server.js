#!/usr/bin/env node
const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8080;
const API_URL = process.env.API_URL || 'http://hermes-api:8000';

// Middleware
app.use(express.static('dist'));
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'hermes-web-ui' });
});

// API proxy - vault search
app.get('/api/vault/search', async (req, res) => {
  try {
    const { q } = req.query;
    if (!q) {
      return res.status(400).json({ error: 'Missing query parameter: q' });
    }
    const response = await axios.get(`${API_URL}/api/vault/search`, {
      params: { q },
      timeout: 5000
    });
    res.json(response.data);
  } catch (error) {
    console.error('API Error:', error.message);
    res.status(500).json({ error: error.message });
  }
});

// API proxy - health
app.get('/api/health', async (req, res) => {
  try {
    const response = await axios.get(`${API_URL}/api/health`, { timeout: 5000 });
    res.json(response.data);
  } catch (error) {
    res.status(503).json({
      status: 'unavailable',
      message: 'Backend API unreachable',
      error: error.message
    });
  }
});

// Serve index.html for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

app.listen(PORT, () => {
  console.log(`🚀 Hermes Web UI listening on http://0.0.0.0:${PORT}`);
  console.log(`📡 Backend API: ${API_URL}`);
});

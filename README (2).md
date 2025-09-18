---
title: n8n Agentic AI Chatbot
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 5.46.0
app_file: app.py
pinned: false
---

# n8n Agentic AI Chatbot

This space contains a frontend interface for an n8n-powered AI chatbot.

## How it works

1. The Gradio interface captures user input
2. Messages are sent to an n8n webhook endpoint
3. n8n processes the message using AI services
4. Response is returned and displayed in the chat

## Setup required

1. Deploy n8n on a cloud service (Railway, Heroku, etc.)
2. Create a webhook workflow in n8n
3. Set the `N8N_WEBHOOK_URL` environment variable
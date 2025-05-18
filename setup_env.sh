#!/bin/bash
# Script to set up environment variables for the Manim video generation pipeline

echo "Setting up environment variables for Manim Video Generation Pipeline"
echo "-------------------------------------------------------------------"
echo

# Check if .env file exists
if [ -f .env ]; then
  echo "Found existing .env file."
  echo "Would you like to overwrite it? (y/n)"
  read overwrite
  if [[ "$overwrite" != "y" && "$overwrite" != "Y" ]]; then
    echo "Keeping existing .env file."
    exit 0
  fi
fi

echo "Please enter your OpenAI API key (starts with 'sk-'):"
read openai_key

# Validate OpenAI key format
if [[ ! "$openai_key" =~ ^sk- ]]; then
  echo "Error: OpenAI API key should start with 'sk-'"
  exit 1
fi

# Write to .env file
echo "OPENAI_API_KEY=\"$openai_key\"" > .env

echo
echo "Environment variables saved to .env file."
echo
echo "To load these variables into your shell session, run:"
echo "  source .env"
echo
echo "Add this line to your .bashrc or .zshrc to load them automatically:"
echo "  [ -f \"$(pwd)/.env\" ] && source \"$(pwd)/.env\""
echo
echo "Setup complete!"
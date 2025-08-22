# Troubleshooting Guide

## OpenAI API Error: "Expecting value: line 1 column 1 (char 0)"

This error occurs when the OpenAI API key is not properly configured or the API response is malformed.

### Quick Fix

1. **Set your OpenAI API key as an environment variable:**

   ```bash
   export OPENAI_API_KEY="your_actual_api_key_here"
   ```

2. **Or create a .env file in your project root:**

   ```bash
   echo "OPENAI_API_KEY=your_actual_api_key_here" > .env
   ```

3. **Restart your Flask application**

### Detailed Steps

1. **Get your OpenAI API key:**

   - Go to [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create a new API key or copy an existing one

2. **Configure the environment:**

   - Option A: Set environment variable before running the app
   - Option B: Use the setup script: `python setup_env.py`
   - Option C: Manually create a `.env` file

3. **Verify configuration:**

   ```bash
   echo $OPENAI_API_KEY
   ```

4. **Test the application:**
   - Restart your Flask app
   - Try sending a message through the chat interface

### Common Issues

- **Missing API key**: The most common cause - ensure `OPENAI_API_KEY` is set
- **Invalid API key**: Check that your API key is correct and active
- **Rate limiting**: If you're making many requests, you might hit rate limits
- **Network issues**: Ensure your application can reach the OpenAI API

### Alternative Solutions

If you continue having issues:

1. **Check OpenAI API status**: [https://status.openai.com/](https://status.openai.com/)
2. **Verify your account**: Ensure your OpenAI account is active and has credits
3. **Check API usage**: Monitor your API usage in the OpenAI dashboard

### Getting Help

- Check the Flask application logs for more detailed error messages
- Verify your environment variables are loaded correctly
- Test with a simple OpenAI API call to isolate the issue

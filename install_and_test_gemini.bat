@echo off
echo ================================================================================
echo GEMINI INSTALLATION AND TEST
echo ================================================================================
echo.

echo Step 1: Installing google-genai package...
pip install google-genai
echo.

echo Step 2: Setting API Key...
set GEMINI_API_KEY=AIzaSyDkYkUeAK9--PAvwCu184VoAA4uDAxVQbw
echo API Key set: %GEMINI_API_KEY%
echo.

echo Step 3: Running simple Gemini test...
python test_gemini_simple.py
echo.

echo ================================================================================
echo Test Complete!
echo ================================================================================
pause


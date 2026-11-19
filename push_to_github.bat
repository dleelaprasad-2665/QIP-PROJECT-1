@echo off
title Push Construction AI Project to GitHub
echo ================================================================
echo Pushing Construction AI Project to GitHub
echo Repository: https://github.com/dleelaprasad-2665/QIP-PROJECT-1.git
echo Branch:     main
echo ================================================================
echo.
echo When prompted:
echo   - Username: dleelaprasad-2665 (or your GitHub email)
echo   - Password: Your GitHub Personal Access Token (PAT)
echo.
"C:\Users\91855\.mingit\cmd\git.exe" push -u origin main
echo.
if %ERRORLEVEL% EQU 0 (
    echo ================================================================
    echo SUCCESS: Project pushed to GitHub successfully!
    echo ================================================================
) else (
    echo ================================================================
    echo Push failed. If using password authentication, please generate a
    echo GitHub Personal Access Token at https://github.com/settings/tokens
    echo and paste it when prompted for password.
    echo ================================================================
)
echo.
pause

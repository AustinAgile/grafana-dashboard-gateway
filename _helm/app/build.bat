@echo off
set repo=%~dp0/../../../../chart-repo
set pwd=%cd%
rem echo %pwd%
helm package -u -d %repo% %~dp0
helm repo index %~dp0/../../../../chart-repo
cd %repo%
git add --all
git commit --all -m "update"
git push --all
cd %pwd%

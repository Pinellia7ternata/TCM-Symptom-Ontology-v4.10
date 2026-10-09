@echo off
REM ============================================================
REM  TCM-SO  |  Push the three SSSOM mapping sets to GitHub
REM  Repo : Pinellia7ternata/TCM-Symptom-Ontology-v4.8  (branch: main)
REM  Files: mappings/TCM-SO-HPO.sssom.tsv        (649 mappings)
REM          mappings/TCM-SO-SNOMEDCT.sssom.tsv   (707 mappings)
REM          mappings/TCM-SO-ICD11.sssom.tsv      (973 mappings)
REM  Run  : double-click this file, or run from cmd in this folder.
REM         When git asks for credentials:
REM             Username: Pinellia7ternata
REM             Password: <your GitHub Personal Access Token (PAT)>
REM ============================================================
setlocal
cd /d "%~dp0"
echo === TCM-SO SSSOM push helper ===
echo Working dir: %CD%
echo.

if not exist "_push\.git" (
  echo [1/4] Cloning remote repository into _push ...
  git clone https://github.com/Pinellia7ternata/TCM-Symptom-Ontology-v4.8.git _push
  if errorlevel 1 goto :err
) else (
  echo [1/4] _push already cloned, skipping clone.
)

echo [2/4] Copying SSSOM files ...
copy /Y "mappings\TCM-SO-HPO.sssom.tsv"      "_push\mappings\" >nul
copy /Y "mappings\TCM-SO-SNOMEDCT.sssom.tsv" "_push\mappings\" >nul
copy /Y "mappings\TCM-SO-ICD11.sssom.tsv"    "_push\mappings\" >nul

cd "_push"
echo [3/4] Staging and committing ...
git add "mappings/TCM-SO-HPO.sssom.tsv" "mappings/TCM-SO-SNOMEDCT.sssom.tsv" "mappings/TCM-SO-ICD11.sssom.tsv"
git commit -m "Add SSSOM mapping sets for HPO, SNOMED CT and ICD-11 (2,329 mappings)"

echo [4/4] Pushing to origin main ...
git push origin main
if errorlevel 1 goto :err

echo.
echo === SUCCESS: SSSOM mapping sets pushed. ===
goto :end

:err
echo.
echo *** FAILED. Read the messages above. Common fixes: ***
echo   - git not on PATH  -> install Git for Windows
echo   - auth failed      -> use a PAT as the password
echo   - divergent branch -> run "git pull --rebase origin main" inside _push

:end
cd /d "%~dp0"
echo.
pause

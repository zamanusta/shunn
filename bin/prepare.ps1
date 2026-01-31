param(
    [string]$infile,
    [string]$outfile
)

$ErrorActionPreference = "Stop"

# --- GTK3 FIX FOR WINDOWS ---
$gtkPath = "C:\Program Files\GTK3-Runtime Win64\bin"
if (Test-Path $gtkPath) {
    if ($env:PATH -notlike "*$gtkPath*") {
        Write-Host "Found GTK3. Adding to PATH for this session..."
        $env:PATH = "$gtkPath;$env:PATH"
    }
}
# -----------------------------

if ([string]::IsNullOrWhiteSpace($infile)) {
    Write-Host "Usage: .\bin\prepare.ps1 <input> [outfile]"
    exit 1
}

if (-not (Test-Path $infile)) {
    Write-Host "File not found: $infile"
    exit 1
}

if ([string]::IsNullOrWhiteSpace($outfile)) {
    $x = Split-Path $infile -Leaf
    if ($x -match '^(.*)\.[^.]*$') { $basename = $Matches[1] } else { $basename = $x }
    
    if (-not (Test-Path "outputs")) {
        New-Item -ItemType Directory -Force -Path "outputs" | Out-Null
    }
    $outfile = "outputs/$basename.pdf"
}

$metadata_option = ""
if (Test-Path "metadata.yaml") {
    $metadata_option = "--metadata-file=metadata.yaml"
}

# 1. Check for Python
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH."
    exit 1
}

# 2. Run Python render script
Write-Host "Running render (Python)..."
python support/render.py "$infile"
if ($LASTEXITCODE -ne 0) { 
    Write-Error "Render failed"
    exit $LASTEXITCODE 
}

# 3. Process and Output
$processScript = Join-Path $PSScriptRoot "process.ps1"

Write-Host "Generating PDF to $outfile..."

try {
    # Check WeasyPrint version to ensure it runs
    $weasyVersion = weasyprint --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "WeasyPrint check failed even after adding GTK3."
    }

    # ENCODING FIX:
    # Instead of piping (which causes encoding issues in PowerShell),
    # we generate a temporary HTML file first using Pandoc directly.
    $tempHtml = [System.IO.Path]::GetTempFileName() + ".html"
    
    & $processScript -infile "$infile" -metadata_option "$metadata_option" -outfile "$tempHtml"
    
    if ($LASTEXITCODE -ne 0) {
        throw "Pandoc HTML generation failed."
    }

    # Now run WeasyPrint on the temp file
    weasyprint "$tempHtml" "$outfile"
    
    if ($LASTEXITCODE -ne 0) {
        throw "WeasyPrint execution failed."
    }
    
    # Cleanup
    if (Test-Path $tempHtml) { Remove-Item $tempHtml }

    Write-Host "Done. PDF created at $outfile"

} catch {
    Write-Warning "PDF generation failed."
    Write-Warning "Error details: $_"
    
    # If temp file exists, move it to output as fallback
    if ($tempHtml -and (Test-Path $tempHtml)) {
         # Change outfile extension to .html
        if ($outfile -match '\.pdf$') {
            $outfileHtml = $outfile -replace '\.pdf$', '.html'
        } else {
            $outfileHtml = "$outfile.html"
        }
        
        Move-Item $tempHtml $outfileHtml -Force
        Write-Warning "Falling back: HTML version preserved at $outfileHtml"
    }
}

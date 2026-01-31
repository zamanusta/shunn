param(
    [string]$infile,
    [string]$metadata_option,
    [string]$outfile  # Optional output file path
)

$currentDir = (Get-Location).Path
# Convert backslashes to forward slashes for Pandoc
$currentDir = $currentDir -replace '\\', '/'

$pandocArgs = @(
    "-f", "markdown+smart"
)

if (-not [string]::IsNullOrWhiteSpace($metadata_option)) {
    $pandocArgs += $metadata_option
}

$pandocArgs += "-L", "$currentDir/support/wordcount.lua"
$pandocArgs += "--strip-comments"
$pandocArgs += "-t", "html"
$pandocArgs += "--template", "$currentDir/templates/template.html5"
$pandocArgs += "-s", "$infile"

# Fix for WeasyPrint on Windows: It requires file:/// URI for local resources
$cssAnsPath = "$currentDir/rendered/manuscript.css"
$cssUri = "file:///$cssAnsPath"

$pandocArgs += "-c", "$cssUri"

if (-not [string]::IsNullOrWhiteSpace($outfile)) {
    $pandocArgs += "-o", "$outfile"
}

& pandoc $pandocArgs

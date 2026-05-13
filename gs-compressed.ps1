# Check if "compressed" directory exists, create it if not
if (-not (Test-Path -Path "compressed" -PathType Container)) {
    New-Item -ItemType Directory -Path "compressed" | Out-Null
    Write-Host "Created 'compressed' directory."
} else {
    Write-Host "'compressed' directory already exists! Proceeding..."
}

# Process each PDF in the current directory
Get-ChildItem -Filter "*.pdf" | ForEach-Object {
    $inputFile = $_.Name
    $outputFile = Join-Path "compressed" $_.Name

    Write-Host "Compressing: $inputFile"

    Start-Process gswin64c -ArgumentList "-sDEVICE=pdfwrite -dQUIET -dCompatibilityLevel=1.7 -dPDFSETTINGS=/ebook -dNOPAUSE -dBATCH -sOUTPUTFILE=""$outputFile"" ""$inputFile""" -Wait -NoNewWindow
}

Write-Host "Done! Compressed files are in the 'compressed' folder."
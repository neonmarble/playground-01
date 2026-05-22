<#
.SYNOPSIS

Compresses PDF files in the current directory using Ghostscript.

.DESCRIPTION

Processes all *.pdf files and writes compressed copies to a subdirectory.

.PARAMETER OutputDir
Destination directory for compressed PDFs. Defaults to "compressed".

.PARAMETER PdfSettings
Ghostscript PDFSETTINGS preset. One of: /screen, /ebook, /printer, /prepress, /default.
Defaults to "/ebook".

.PARAMETER GsExe
Path to the Ghostscript executable. Accepts a name on PATH (e.g. "gswin64c") or a full
path (e.g. "C:\Program Files\gs\bin\gswin64c.exe"). Defaults to "gswin64c".

.INPUTS

None. You cannot pipe input to this script.

.OUTPUTS

None. This script writes files to disk and does not generate pipeline output.

.EXAMPLE

PS> .\gs-compressed.ps1

Compresses all PDFs in the current directory using the default /ebook settings.

.EXAMPLE

PS> .\gs-compressed.ps1 -PdfSettings /screen -OutputDir small

Compresses PDFs with /screen preset and writes output to a "small" subdirectory.
#>

[CmdletBinding()]
param(
	[string]$OutputDir = 'compressed',
	[ValidateSet('/screen', '/ebook', '/printer', '/prepress', '/default')]
	[string]$PdfSettings = '/ebook',
	[string]$GsExe = 'gswin64c'
)

$ErrorActionPreference = 'Stop'

# Locate Ghostscript
$gsPath = Get-Command -Name $GsExe -CommandType Application -ErrorAction Stop |
	Select-Object -ExpandProperty Source
Write-Verbose "Using Ghostscript: $gsPath"

# Collect PDFs
$pdfFiles = @(Get-ChildItem -LiteralPath . -Filter '*.pdf' -File)
if ($pdfFiles.Count -eq 0) {
	Write-Host 'No PDF files found in the current directory.'
	return
}

# Ensure output directory (only after confirming PDFs exist)
if (-not (Test-Path -LiteralPath $OutputDir -PathType Container)) {
	New-Item -ItemType Directory -Path $OutputDir | Out-Null
	Write-Verbose "Created '$OutputDir' directory."
}

# Create temp directory for files with special characters
$tempDir = Join-Path $env:TEMP "gs-compress-temp-$(Get-Date -Format 'yyyyMMddHHmmss')"
New-Item -ItemType Directory -Path $tempDir | Out-Null
try {
	# Process PDFs
	$i = 0
	$total = $pdfFiles.Count
	Write-Host "Processing $total PDF file(s)..."

	$pdfFiles | ForEach-Object -Begin { $i = 0 } -Process {
		# Skip non-PDF files
		if ($_.Extension -ne '.pdf') {
			return
		}

		$i++
		$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
		$percent = [math]::Floor(($i / $total) * 100)

		Write-Progress -Activity 'Compressing PDFs' `
			-Status "File $i of $total [$percent%]" `
			-CurrentOperation $_.Name `
			-PercentComplete $percent

		Write-Host "[$timestamp] Compressing: $($_.Name)"

		$outputFile = Join-Path $OutputDir $_.Name

		# Sanitize filename for Ghostscript (handles %, &, spaces, etc.)
		$safeName = "$($_.BaseName -replace '[^a-zA-Z0-9._-]', '_').pdf"
		$tempInput = Join-Path $tempDir $safeName
		$tempOutput = Join-Path $tempDir "compressed_$safeName"

		Copy-Item $_.FullName -Destination $tempInput -Force

		$gsArgs = @(
			'-sDEVICE=pdfwrite',
			'-dCompatibilityLevel=1.7',
			"-dPDFSETTINGS=$PdfSettings",
			'-dNOPAUSE',
			'-dBATCH',
			"-sOutputFile=$tempOutput",
			$tempInput
		)

		& $gsPath $gsArgs
		if ($LASTEXITCODE -ne 0) {
			throw "Ghostscript failed on '$($_.Name)' (exit code: $LASTEXITCODE)"
		}

		# Copy result back with original filename
		Copy-Item $tempOutput -Destination $outputFile -Force
	} -End {
		Write-Progress -Activity 'Compressing PDFs' -Completed
	}
}
finally {
	# Clean up temp directory
	if (Test-Path -LiteralPath $tempDir -PathType Container) {
		Remove-Item $tempDir -Recurse -Force
	}
}

Write-Host "Done! Compressed files are in '$OutputDir'."

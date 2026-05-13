<#	
.SYNOPSIS
	Compresses PDF files in the current directory using Ghostscript.
.DESCRIPTION
	Processes all *.pdf files and writes compressed copies to a subdirectory.
.PARAMETER OutputDir
	Destination directory for compressed PDFs. Defaults to "compressed".
.PARAMETER PdfSettings
	Ghostscript PDFSETTINGS preset. One of: /screen, /ebook, /printer, /prepress, /default.
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
	exit 0
}

# Ensure output directory (only after confirming PDFs exist)
if (-not (Test-Path -LiteralPath $OutputDir -PathType Container)) {
	New-Item -ItemType Directory -Path $OutputDir | Out-Null
	Write-Verbose "Created '$OutputDir' directory."
}

# Process PDFs
$pdfFiles | ForEach-Object {
	$outputFile = Join-Path $OutputDir $_.Name
	Write-Verbose "Compressing: $($_.Name)"

	$gsArgs = @(
		'-sDEVICE=pdfwrite',
		'-dQUIET',
		'-dCompatibilityLevel=1.7',
		"-dPDFSETTINGS=$PdfSettings",
		'-dNOPAUSE',
		'-dBATCH',
		"-sOutputFile=$outputFile",
		$_.FullName
	)

	& $gsPath $gsArgs
	if ($LASTEXITCODE -ne 0) {
		Write-Error "Ghostscript failed on '$($_.Name)' (exit code: $LASTEXITCODE)"
	}
}

Write-Host "Done! Compressed files are in '$OutputDir'."

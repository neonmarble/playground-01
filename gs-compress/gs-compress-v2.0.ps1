<#
.SYNOPSIS

Compresses PDF files in the current directory using Ghostscript.

.DESCRIPTION

Processes all *.pdf files and writes compressed copies to a subdirectory.
Displays per-file compression ratios and an overall summary upon completion.

Wrapped in the advanced function Compress-Pdf for reusability and testability.

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

PS> .\gs-compress-v2.0.ps1

Compresses all PDFs in the current directory using the default /ebook settings.

.EXAMPLE

PS> .\gs-compress-v2.0.ps1 -PdfSettings /screen -OutputDir small

Compresses PDFs with /screen preset and writes output to a "small" subdirectory.

.EXAMPLE

PS> .\gs-compress-v2.0.ps1 -WhatIf

Shows what would happen without actually compressing any files.

.EXAMPLE

PS> .\gs-compress-v2.0.ps1 -Confirm

Prompts for confirmation before compressing each file.

.LINK

https://ghostscript.com
#>

[CmdletBinding(SupportsShouldProcess)]
param(
	[string]$OutputDir = 'compressed',
	[ValidateSet('/screen', '/ebook', '/printer', '/prepress', '/default')]
	[string]$PdfSettings = '/ebook',
	[string]$GsExe = 'gswin64c'
)

function Compress-Pdf {
	[CmdletBinding(SupportsShouldProcess)]
	param(
		[Parameter()]
		[string]$OutputDir = 'compressed',

		[Parameter()]
		[ValidateSet('/screen', '/ebook', '/printer', '/prepress', '/default')]
		[string]$PdfSettings = '/ebook',

		[Parameter()]
		[string]$GsExe = 'gswin64c'
	)

	$ErrorActionPreference = 'Stop'
	$InformationPreference = 'Continue'

	# Capture $PSCmdlet so it's accessible inside nested scriptblocks (ForEach-Object -Process)
	$caller = $PSCmdlet

	# ── Locate Ghostscript ────────────────────────────────────────────────
	$gsPath = Get-Command -Name $GsExe -CommandType Application -ErrorAction Stop |
		Select-Object -ExpandProperty Source
	Write-Verbose "Using Ghostscript: $gsPath"

	# ── Collect PDFs ──────────────────────────────────────────────────────
	$pdfFiles = @(Get-ChildItem -LiteralPath . -Filter '*.pdf' -File)
	if ($pdfFiles.Count -eq 0) {
		Write-Information 'No PDF files found in the current directory.'
		return
	}

	# ── Ensure output directory ───────────────────────────────────────────
	# Resolve to absolute path early so all subsequent operations are unambiguous.
	$resolvedOutputDir = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputDir)

	if (-not (Test-Path -LiteralPath $resolvedOutputDir -PathType Container)) {
		if ($caller.ShouldProcess($resolvedOutputDir, 'Create output directory')) {
			# Use .NET method — New-Item lacks -LiteralPath in PS 5.1,
			# and New-Item -Path would misinterpret brackets in directory names.
			[System.IO.Directory]::CreateDirectory($resolvedOutputDir) | Out-Null
			Write-Verbose "Created '$resolvedOutputDir' directory."
		}
	}

	# ── Create temp directory (GUID avoids collisions) ────────────────────
	$tempDir = Join-Path $env:TEMP "gs-compress-$([guid]::NewGuid().ToString('N'))"
	[System.IO.Directory]::CreateDirectory($tempDir) | Out-Null

	# ── Process PDFs ──────────────────────────────────────────────────────
	$total = $pdfFiles.Count
	$totalOriginalSize = 0
	$totalCompressedSize = 0
	Write-Information "Processing $total PDF file(s)..."

	try {
		$i = 0
		$pdfFiles | ForEach-Object -Begin { $i = 0 } -Process {
			$i++
			$percent = [math]::Floor(($i / $total) * 100)

			Write-Progress -Activity 'Compressing PDFs' `
				-Status "File $i of $total [$percent%]" `
				-CurrentOperation $_.Name `
				-PercentComplete $percent

			if (-not $caller.ShouldProcess($_.Name, 'Compress PDF')) {
				return
			}

			Write-Information "[$i/$total] Compressing: $($_.Name)"

			$outputFile = Join-Path $resolvedOutputDir $_.Name

			# Sanitize filename for Ghostscript (handles %, &, spaces, [], etc.)
			$safeName = "$($_.BaseName -replace '[^a-zA-Z0-9._-]', '_').pdf"
			$tempInput  = Join-Path $tempDir $safeName
			$tempOutput = Join-Path $tempDir "compressed_$safeName"

			Copy-Item -LiteralPath $_.FullName -Destination $tempInput -Force

			$gsArgs = @(
				'-sDEVICE=pdfwrite'
				'-dCompatibilityLevel=1.7'
				"-dPDFSETTINGS=$PdfSettings"
				'-dNOPAUSE'
				'-dBATCH'
				"-sOutputFile=$tempOutput"
				$tempInput
			)

			# Suppress Ghostscript's noisy stdout (copyright notices, font
			# substitution messages, repair warnings) — it writes these to
			# stdout, NOT stderr, so 2> wouldn't capture them. Capture to
			# a temp file so we can include details on failure.
			$gsOutputFile = Join-Path $tempDir "gs_output_$i.txt"
			& $gsPath @gsArgs 1>$gsOutputFile 2>&1
			if ($LASTEXITCODE -ne 0) {
				$gsLog = if (Test-Path -LiteralPath $gsOutputFile) {
					(Get-Content -LiteralPath $gsOutputFile -Raw).Trim()
				} else {
					'(no output captured)'
				}
				throw "Ghostscript failed on '$($_.Name)' (exit code: $LASTEXITCODE).`n$gsLog"
			}

			# Copy result back with original filename
			Copy-Item -LiteralPath $tempOutput -Destination $outputFile -Force

			# ── Compression ratio reporting ──────────────────────────────
			$originalSize   = $_.Length
			$compressedSize = (Get-Item -LiteralPath $outputFile).Length
			$totalOriginalSize   += $originalSize
			$totalCompressedSize += $compressedSize

			if ($originalSize -gt 0) {
				$ratio = [math]::Round((1 - $compressedSize / $originalSize) * 100, 1)
			}
			else {
				$ratio = 0
			}

			$origKB = [math]::Round($originalSize / 1KB, 1)
			$compKB = [math]::Round($compressedSize / 1KB, 1)
			Write-Information ("  {0}: {1}KB -> {2}KB ({3}% reduction)" -f $_.Name, $origKB, $compKB, $ratio)
		} -End {
			Write-Progress -Activity 'Compressing PDFs' -Completed
		}
	}
	finally {
		# Clean up temp directory (use .NET to avoid -WhatIf propagation
		# into cleanup code — cleanup must always run even under -WhatIf)
		if ([System.IO.Directory]::Exists($tempDir)) {
			[System.IO.Directory]::Delete($tempDir, $true) | Out-Null
		}
	}

	# ── Summary ───────────────────────────────────────────────────────────
	if ($totalOriginalSize -gt 0) {
		$totalRatio   = [math]::Round((1 - $totalCompressedSize / $totalOriginalSize) * 100, 1)
		$totalOrigMB  = [math]::Round($totalOriginalSize / 1MB, 2)
		$totalCompMB  = [math]::Round($totalCompressedSize / 1MB, 2)
		Write-Information ("`nDone! {0} -> {1} ({2}% total reduction)" -f "$totalOrigMB MB", "$totalCompMB MB", $totalRatio)
	}
	else {
		Write-Information "`nDone! Compressed files are in '$resolvedOutputDir'."
	}
}

# ── Invoke the function ───────────────────────────────────────────────────
Compress-Pdf @PSBoundParameters

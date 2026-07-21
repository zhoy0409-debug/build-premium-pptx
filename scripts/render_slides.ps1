<#
.SYNOPSIS
Render specific slides of a deck to PNG, for shortlisting layouts and for render QA.

.DESCRIPTION
Rendering a 200-slide layout bank in full is wasteful when only a shortlist matters.
This exports just the requested slides via PowerPoint COM (Windows), falling back to
LibreOffice for a whole-deck PDF when PowerPoint is unavailable.

.EXAMPLE
./render_slides.ps1 -Path 'D:\lib\report.pptx' -Slides 7,10,31 -OutDir work\thumbs

.EXAMPLE
./render_slides.ps1 -Path 'D:\lib\report.pptx' -OutDir work\thumbs   # every slide
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Path,
    [int[]]$Slides,
    [string]$OutDir = 'work/thumbs',
    [int]$Width = 1600,
    [int]$Height = 900
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Path)) { throw "Deck not found: $Path" }
$deck = (Resolve-Path -LiteralPath $Path).Path
if (-not (Test-Path -LiteralPath $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
}
$outRoot = (Resolve-Path -LiteralPath $OutDir).Path
$stem = [IO.Path]::GetFileNameWithoutExtension($deck)

function Invoke-LibreOfficeFallback {
    $soffice = (Get-Command soffice, soffice.com, libreoffice -ErrorAction SilentlyContinue |
                Select-Object -First 1).Source
    if (-not $soffice) {
        throw 'Neither PowerPoint COM nor LibreOffice is available; cannot render.'
    }
    Write-Warning 'PowerPoint COM unavailable; exporting the whole deck to PDF instead.'
    $pdf = Join-Path $outRoot "$stem.pdf"
    # Embedded fonts in purchased decks make soffice chatter on stderr ("EOT out of
    # spec"). That is a warning, not a failure, so judge the run by the artefact.
    & $soffice --headless --convert-to pdf --outdir $outRoot $deck 2>&1 | Out-Null
    if (-not (Test-Path -LiteralPath $pdf)) {
        throw "LibreOffice did not produce $pdf; the deck could not be rendered."
    }
    Write-Warning 'Output is a PDF, not per-slide PNGs; rasterise it for image QA.'
    Write-Output $pdf
}

function New-PowerPointApp {
    # A crashed prior run can leave the COM server rejecting calls
    # (RPC_E_CALL_REJECTED) for a short while, so treat the first refusal as
    # transient rather than falling straight through to a whole-deck PDF.
    foreach ($attempt in 1..3) {
        try {
            return New-Object -ComObject PowerPoint.Application
        } catch {
            if ($attempt -eq 3) { return $null }
            Write-Warning "PowerPoint COM refused the call (attempt $attempt/3); retrying."
            Start-Sleep -Seconds 5
        }
    }
}

$app = New-PowerPointApp
$presentation = $null
if (-not $app) {
    Invoke-LibreOfficeFallback
    return
}

try {
    # 2 = msoFalse: keep the file read-only and untitled so the master is never altered.
    $presentation = $app.Presentations.Open($deck, 2, 2, 0)
    $total = $presentation.Slides.Count
    $targets = if ($Slides) { $Slides | Sort-Object -Unique } else { 1..$total }

    foreach ($n in $targets) {
        if ($n -lt 1 -or $n -gt $total) {
            Write-Warning "Slide $n is outside 1..$total; skipped."
            continue
        }
        $png = Join-Path $outRoot ("{0}-slide{1:d3}.png" -f $stem, $n)
        $presentation.Slides.Item($n).Export($png, 'PNG', $Width, $Height)
        Write-Output $png
    }
} finally {
    if ($presentation) { $presentation.Close() }
    if ($app) { $app.Quit() }
    [GC]::Collect()
}

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
    & $soffice --headless --convert-to pdf --outdir $outRoot $deck | Out-Null
    Write-Output (Join-Path $outRoot "$stem.pdf")
}

$app = $null
$presentation = $null
try {
    $app = New-Object -ComObject PowerPoint.Application
} catch {
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

\
    param(
      [string]$RepoRoot = (Get-Location).Path
    )

    $ErrorActionPreference = "Stop"

    function Find-IndexHtml {
      $candidates = @(
        "web/index.html",
        "web/dist/index.html",
        "web/public/index.html",
        "index.html"
      )
      foreach ($rel in $candidates) {
        $p = Join-Path $RepoRoot $rel
        if (Test-Path $p) { return $p }
      }
      $hit = Get-ChildItem -Path $RepoRoot -Recurse -File -Filter "index.html" -ErrorAction SilentlyContinue | Select-Object -First 1
      if ($hit) { return $hit.FullName }
      return $null
    }

    $indexPath = Find-IndexHtml
    if (-not $indexPath) {
      Write-Host "ERROR: Could not find index.html in repo." -ForegroundColor Red
      exit 1
    }

    Write-Host "Found index.html: $indexPath"

    $content = Get-Content $indexPath -Raw -Encoding UTF8
    if ($content -match "AAS TABLEAU IFRAME GUARD\+ v19") {
      Write-Host "Guard v19 already installed. Nothing to do." -ForegroundColor Yellow
      exit 0
    }

    $guard = Get-Content (Join-Path $RepoRoot "instructions19/guard_v19.html") -Raw -Encoding UTF8

    if ($content -match "</body>") {
      $patched = $content -replace "</body>", ($guard + "`n</body>")
    } else {
      $patched = $content + "`n" + $guard + "`n"
    }

    Set-Content -Path $indexPath -Value $patched -Encoding UTF8
    Write-Host "✅ Installed Guard v19. Hard refresh your browser to load it." -ForegroundColor Green

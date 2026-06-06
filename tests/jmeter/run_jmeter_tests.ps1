param(
    [string]$JMeter = "jmeter",
    [int[]]$Users = @(10, 30, 50, 100),
    [int]$RampUp = 30,
    [int]$ThinkTimeMs = 1000,
    [int]$ShortDuration = 600,
    [int]$LongDuration = 900,
    [string]$ExperimentPrefix = "EXP"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$TestPlan = Join-Path $PSScriptRoot "online_boutique_test_plan.jmx"
$RawDir = Join-Path $RepoRoot "results\testing\raw_jmeter"
New-Item -ItemType Directory -Force $RawDir | Out-Null

$rawFiles = New-Object System.Collections.Generic.List[string]

for ($i = 0; $i -lt $Users.Count; $i++) {
    $userCount = $Users[$i]
    $duration = if ($userCount -ge 50) { $LongDuration } else { $ShortDuration }
    $scenario = "jmeter_${userCount}_users"
    $experimentId = "{0}_{1:D3}" -f $ExperimentPrefix, ($i + 1)
    $rawFile = Join-Path $RawDir "$scenario.jtl"
    if (Test-Path $rawFile) {
        Remove-Item -LiteralPath $rawFile -Force
    }

    Write-Host "Running $scenario, duration=${duration}s, experiment_id=$experimentId"

    & $JMeter `
      -n `
      -t $TestPlan `
      -l $rawFile `
      "-JCONCURRENT_USERS=$userCount" `
      "-JSCENARIO=$scenario" `
      "-JEXPERIMENT_ID=$experimentId" `
      "-JDURATION=$duration" `
      "-JRAMP_UP=$RampUp" `
      "-JTHINK_TIME_MS=$ThinkTimeMs"

    if ($LASTEXITCODE -ne 0) {
        throw "JMeter failed for $scenario with exit code $LASTEXITCODE. Raw result was not generated."
    }
    if (-not (Test-Path $rawFile)) {
        throw "JMeter finished but raw result file was not generated: $rawFile"
    }
    $rawFiles.Add($rawFile)
}

& (Join-Path $PSScriptRoot "convert_jmeter_results.ps1") -InputFiles $rawFiles -ExperimentPrefix $ExperimentPrefix

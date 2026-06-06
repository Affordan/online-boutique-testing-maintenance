param(
    [Parameter(Mandatory = $true)]
    [string[]]$InputFiles,

    [string]$OutputResults = "results/testing/jmeter_results.csv",
    [string]$OutputSummary = "results/testing/jmeter_summary.csv",
    [string]$ExperimentPrefix = "EXP"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$resultRows = New-Object System.Collections.Generic.List[object]
$fileIndex = 0

foreach ($file in $InputFiles) {
    $fileIndex += 1
    $path = Resolve-Path $file
    $rows = Import-Csv $path
    if (-not $rows) {
        continue
    }

    $first = $rows[0]
    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($path)
    $scenario = if ($first.scenario) { $first.scenario } else { $fileName }
    $experimentId = if ($first.experiment_id) { $first.experiment_id } else { "{0}_{1:D3}" -f $ExperimentPrefix, $fileIndex }
    $concurrentUsers = if ($first.concurrent_users) {
        [int]$first.concurrent_users
    } elseif ($fileName -match 'jmeter_(\d+)_users') {
        [int]$Matches[1]
    } else {
        0
    }

    $startMs = ($rows | ForEach-Object { [int64]$_.timeStamp } | Measure-Object -Minimum).Minimum
    $endMs = ($rows | ForEach-Object { [int64]$_.timeStamp + [int64]$_.elapsed } | Measure-Object -Maximum).Maximum
    $durationSeconds = [Math]::Max(1, ($endMs - $startMs) / 1000)
    $throughput = [Math]::Round($rows.Count / $durationSeconds, 3)

    foreach ($row in $rows) {
        $labelParts = $row.label -split "\|", 2
        $service = if ($labelParts.Count -ge 1) { $labelParts[0] } else { "unknown" }
        $endpoint = if ($labelParts.Count -ge 2) { $labelParts[1] } else { $row.label }
        $timestamp = [DateTimeOffset]::FromUnixTimeMilliseconds([int64]$row.timeStamp).LocalDateTime.ToString("yyyy-MM-dd HH:mm:ss")
        $statusCode = 0
        if ($row.responseCode -match '^\d+$') {
            $statusCode = [int]$row.responseCode
        }
        $errorMessage = if ($statusCode -eq 0 -and $row.responseCode) {
            "$($row.responseCode): $($row.responseMessage)"
        } else {
            $row.responseMessage
        }

        $resultRows.Add([pscustomobject]@{
            timestamp = $timestamp
            experiment_id = $experimentId
            scenario = $scenario
            service = $service
            endpoint = $endpoint
            concurrent_users = $concurrentUsers
            response_time_ms = [double]$row.elapsed
            latency_ms = [double]$row.Latency
            success = [bool]::Parse($row.success)
            status_code = $statusCode
            error_message = $errorMessage
            throughput = $throughput
            bytes_sent = if ($row.sentBytes) { [int]$row.sentBytes } else { 0 }
            bytes_received = if ($row.bytes) { [int]$row.bytes } else { 0 }
        })
    }
}

$outputResultsPath = Join-Path $RepoRoot $OutputResults
$outputSummaryPath = Join-Path $RepoRoot $OutputSummary
New-Item -ItemType Directory -Force (Split-Path $outputResultsPath) | Out-Null

$resultRows | Export-Csv -NoTypeInformation -Encoding UTF8 $outputResultsPath

$summaryRows = $resultRows |
    Group-Object experiment_id, scenario, service, endpoint, concurrent_users |
    ForEach-Object {
        $group = $_.Group
        $ordered = $group | Sort-Object response_time_ms
        $count = $group.Count
        $p90Index = [Math]::Min($count - 1, [Math]::Ceiling($count * 0.9) - 1)
        $errors = ($group | Where-Object { -not $_.success }).Count
        [pscustomobject]@{
            experiment_id = $group[0].experiment_id
            scenario = $group[0].scenario
            service = $group[0].service
            endpoint = $group[0].endpoint
            concurrent_users = $group[0].concurrent_users
            samples = $count
            average_ms = [Math]::Round(($group | Measure-Object response_time_ms -Average).Average, 2)
            min_ms = ($group | Measure-Object response_time_ms -Minimum).Minimum
            max_ms = ($group | Measure-Object response_time_ms -Maximum).Maximum
            p90_ms = $ordered[$p90Index].response_time_ms
            throughput = $group[0].throughput
            error_percent = [Math]::Round(($errors / $count) * 100, 2)
        }
    }

$summaryRows | Export-Csv -NoTypeInformation -Encoding UTF8 $outputSummaryPath

Write-Host "Wrote $outputResultsPath"
Write-Host "Wrote $outputSummaryPath"

# Test script for the chat endpoint
# Configuration
$baseUrl = "https://autopilot-ventures-1027187250482.us-central1.run.app"
$chatUrl = "$baseUrl/api/chat"
$headers = @{ "Content-Type" = "application/json" }

# Test cases
$tests = @(
    @{ lang = "Spanish";   prompt = "¿Cuál es el clima hoy en Madrid?";    expected = "despejado" },
    @{ lang = "French";    prompt = "Donne-moi les dernières nouvelles économiques."; expected = "nouvelles" },
    @{ lang = "Chinese";   prompt = "请告诉我今天的汇率。";                    expected = "汇率" },
    @{ lang = "Arabic";    prompt = "ما هي أخبار الرياضة اليوم؟";            expected = "كرة القدم" },
    @{ lang = "Hindi";     prompt = "आज की राजनीति पर कुछ बताइए।";         expected = "संसद" }
)

Write-Host "🧪 Testing Chat Endpoint" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

$results = @()

foreach ($test in $tests) {
    Write-Host "`n📝 Testing $($test.lang): $($test.prompt)" -ForegroundColor Yellow
    
    try {
        # Prepare request body
        $body = @{
            prompt = $test.prompt
            language = $test.lang.Substring(0,2).ToLower()  # Get language code
        } | ConvertTo-Json -Depth 5
        
        # Make request
        $start = Get-Date
        $response = Invoke-RestMethod -Method POST -Uri $chatUrl -Headers $headers -Body $body -TimeoutSec 30
        $end = Get-Date
        $duration = ($end - $start).TotalSeconds
        
        $responseText = $response.response
        
        # Check if expected content is in response
        if ($responseText -like "*$($test.expected)*") {
            $status = "✅ PASS"
        } else {
            $status = "❌ MISMATCH"
        }
        
        Write-Host "   Status: $status" -ForegroundColor Green
        Write-Host "   Response: $responseText" -ForegroundColor White
        Write-Host "   Time: $duration sec" -ForegroundColor Gray
        
        $results += [PSCustomObject]@{
            Language = $test.lang
            Status = $status
            Response = $responseText
            Time = "$duration sec"
        }
        
    } catch {
        Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        
        $results += [PSCustomObject]@{
            Language = $test.lang
            Status = "❌ Error"
            Response = $_.Exception.Message
            Time = "N/A"
        }
    }
}

# Summary
Write-Host "`n" + "=" * 50 -ForegroundColor Cyan
Write-Host "📊 Test Summary" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

$results | Format-Table -AutoSize

# Count results
$passed = ($results | Where-Object { $_.Status -like "*PASS*" }).Count
$total = $results.Count

Write-Host "`n✅ Passed: $passed/$total" -ForegroundColor Green
Write-Host "❌ Failed: $($total - $passed)/$total" -ForegroundColor Red

# Test other endpoints
Write-Host "`n🔍 Testing Other Endpoints" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# Test health endpoint
try {
    $healthResponse = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET -TimeoutSec 10
    Write-Host "✅ Health endpoint: $($healthResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test status endpoint
try {
    $statusResponse = Invoke-RestMethod -Uri "$baseUrl/status" -Method GET -TimeoutSec 10
    Write-Host "✅ Status endpoint: $($statusResponse.system.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Status endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test languages endpoint
try {
    $languagesResponse = Invoke-RestMethod -Uri "$baseUrl/api/languages" -Method GET -TimeoutSec 10
    Write-Host "✅ Languages endpoint: $($languagesResponse.count) languages supported" -ForegroundColor Green
} catch {
    Write-Host "❌ Languages endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
} 
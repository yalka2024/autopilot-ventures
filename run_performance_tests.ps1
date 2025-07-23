# AutoPilot Ventures - Performance Testing Suite
# Run all performance monitoring scripts

Write-Host "🚀 AutoPilot Ventures Performance Testing Suite" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

# Check if platform is running
Write-Host "🔍 Checking if platform is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Platform is running!" -ForegroundColor Green
    } else {
        Write-Host "❌ Platform returned status: $($response.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Platform is not running. Please start the platform first." -ForegroundColor Red
    Write-Host "   Run: python app_autonomous.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "📊 Available Performance Tests:" -ForegroundColor Cyan
Write-Host "1. Quick Performance Check (Fast)" -ForegroundColor White
Write-Host "2. Comprehensive Platform Monitor (Detailed)" -ForegroundColor White
Write-Host "3. Stress Test (Load Testing)" -ForegroundColor White
Write-Host "4. Business Performance Monitor (Revenue Tracking)" -ForegroundColor White
Write-Host "5. Run All Tests (Complete Suite)" -ForegroundColor White

Write-Host ""
$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host "⚡ Running Quick Performance Check..." -ForegroundColor Green
        python quick_performance_check.py
    }
    "2" {
        Write-Host "🔍 Running Comprehensive Platform Monitor..." -ForegroundColor Green
        python platform_performance_monitor.py
    }
    "3" {
        Write-Host "🔥 Running Stress Test..." -ForegroundColor Green
        python stress_test_platform.py
    }
    "4" {
        Write-Host "📈 Running Business Performance Monitor..." -ForegroundColor Green
        python business_performance_monitor.py
    }
    "5" {
        Write-Host "🚀 Running Complete Performance Test Suite..." -ForegroundColor Green
        Write-Host ""
        
        # Quick check first
        Write-Host "Step 1/4: Quick Performance Check" -ForegroundColor Yellow
        python quick_performance_check.py
        Write-Host ""
        
        # Comprehensive monitor
        Write-Host "Step 2/4: Comprehensive Platform Monitor" -ForegroundColor Yellow
        python platform_performance_monitor.py
        Write-Host ""
        
        # Stress test
        Write-Host "Step 3/4: Stress Test" -ForegroundColor Yellow
        python stress_test_platform.py
        Write-Host ""
        
        # Business monitor
        Write-Host "Step 4/4: Business Performance Monitor" -ForegroundColor Yellow
        python business_performance_monitor.py
        Write-Host ""
        
        Write-Host "✅ All performance tests completed!" -ForegroundColor Green
        Write-Host "📁 Check the generated JSON files for detailed results." -ForegroundColor Cyan
    }
    default {
        Write-Host "❌ Invalid choice. Please run the script again." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 Performance testing completed!" -ForegroundColor Green
Write-Host "📊 Results saved to JSON files in the current directory." -ForegroundColor Cyan 
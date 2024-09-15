# PowerShell API Testing Script for Job Application Tracker
# Usage: .\test_api.ps1 -ApiUrl "https://your-service-name.onrender.com"

param(
    [Parameter(Mandatory=$true)]
    [string]$ApiUrl
)

Write-Host "🧪 Testing Job Application Tracker API" -ForegroundColor Cyan
Write-Host "API URL: $ApiUrl" -ForegroundColor Yellow
Write-Host ""

# Function to make HTTP requests and handle responses
function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [string]$Body = $null,
        [string]$TestName
    )
    
    Write-Host "Testing: $TestName" -ForegroundColor Blue
    Write-Host "URL: $Url" -ForegroundColor Gray
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $Headers
            UseBasicParsing = $true
        }
        
        if ($Body) {
            $params.Body = $Body
        }
        
        $response = Invoke-WebRequest @params
        
        if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 201) {
            Write-Host "✅ SUCCESS - Status: $($response.StatusCode)" -ForegroundColor Green
            
            # Try to parse JSON response
            try {
                $jsonResponse = $response.Content | ConvertFrom-Json
                Write-Host "Response:" -ForegroundColor Gray
                Write-Host ($jsonResponse | ConvertTo-Json -Depth 3) -ForegroundColor White
                return $jsonResponse
            } catch {
                Write-Host "Response (non-JSON):" -ForegroundColor Gray
                Write-Host $response.Content -ForegroundColor White
                return $response.Content
            }
        } else {
            Write-Host "⚠️ UNEXPECTED STATUS - Status: $($response.StatusCode)" -ForegroundColor Yellow
            Write-Host $response.Content -ForegroundColor White
            return $null
        }
    } catch {
        Write-Host "❌ FAILED - Error: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        }
        return $null
    }
    
    Write-Host ""
}

# Test 1: Health Check
Write-Host "=" * 60 -ForegroundColor Cyan
$healthResponse = Test-Endpoint -Url "$ApiUrl/health" -TestName "Health Check"

# Test 2: Root Endpoint
Write-Host "=" * 60 -ForegroundColor Cyan
$rootResponse = Test-Endpoint -Url "$ApiUrl/" -TestName "Root Endpoint"

# Test 3: API Documentation (HEAD request to check if accessible)
Write-Host "=" * 60 -ForegroundColor Cyan
try {
    $docsResponse = Invoke-WebRequest -Uri "$ApiUrl/docs" -Method HEAD -UseBasicParsing
    if ($docsResponse.StatusCode -eq 200) {
        Write-Host "✅ SUCCESS - API Documentation is accessible at $ApiUrl/docs" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ FAILED - API Documentation not accessible" -ForegroundColor Red
}

# Test 4: Get All Applications (should return empty array initially)
Write-Host "=" * 60 -ForegroundColor Cyan
$applicationsResponse = Test-Endpoint -Url "$ApiUrl/api/applications" -TestName "Get All Applications"

# Test 5: Create Test Application
Write-Host "=" * 60 -ForegroundColor Cyan
$headers = @{
    "Content-Type" = "application/json"
}
$applicationData = @{
    company = "Test Company"
    position = "Software Engineer"
    status = "applied"
    applied_date = "2024-12-19"
    job_url = "https://example.com/job"
    location = "Remote"
    salary_range = "70000-90000"
    notes = "Test application created via API testing"
} | ConvertTo-Json

$createResponse = Test-Endpoint -Url "$ApiUrl/api/applications" -Method "POST" -Headers $headers -Body $applicationData -TestName "Create Test Application"

# Extract application ID for further tests
$applicationId = $null
if ($createResponse -and $createResponse.id) {
    $applicationId = $createResponse.id
    Write-Host "📝 Created application with ID: $applicationId" -ForegroundColor Green
}

# Test 6: Get Specific Application
if ($applicationId) {
    Write-Host "=" * 60 -ForegroundColor Cyan
    $specificAppResponse = Test-Endpoint -Url "$ApiUrl/api/applications/$applicationId" -TestName "Get Specific Application"
}

# Test 7: Update Application
if ($applicationId) {
    Write-Host "=" * 60 -ForegroundColor Cyan
    $updateData = @{
        company = "Updated Test Company"
        position = "Senior Software Engineer"
        status = "interviewing"
        notes = "Status updated via API testing"
    } | ConvertTo-Json
    
    $updateResponse = Test-Endpoint -Url "$ApiUrl/api/applications/$applicationId" -Method "PUT" -Headers $headers -Body $updateData -TestName "Update Application"
}

# Test 8: Tracking Endpoints
Write-Host "=" * 60 -ForegroundColor Cyan
$statusSummaryResponse = Test-Endpoint -Url "$ApiUrl/api/tracking/status-summary" -TestName "Status Summary"

Write-Host "=" * 60 -ForegroundColor Cyan
$recentActivitiesResponse = Test-Endpoint -Url "$ApiUrl/api/tracking/recent-activities" -TestName "Recent Activities"

Write-Host "=" * 60 -ForegroundColor Cyan
$monthlyStatsResponse = Test-Endpoint -Url "$ApiUrl/api/tracking/monthly-stats" -TestName "Monthly Statistics"

# Test 9: Search and Filter (if implemented)
Write-Host "=" * 60 -ForegroundColor Cyan
$searchResponse = Test-Endpoint -Url "$ApiUrl/api/applications?company=Test" -TestName "Search Applications by Company"

# Test 10: Delete Test Application (cleanup)
if ($applicationId) {
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "🧹 Cleaning up test data..." -ForegroundColor Yellow
    
    try {
        $deleteResponse = Invoke-WebRequest -Uri "$ApiUrl/api/applications/$applicationId" -Method DELETE -UseBasicParsing
        if ($deleteResponse.StatusCode -eq 200 -or $deleteResponse.StatusCode -eq 204) {
            Write-Host "✅ SUCCESS - Test application deleted" -ForegroundColor Green
        } else {
            Write-Host "⚠️ WARNING - Delete returned status: $($deleteResponse.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ FAILED - Could not delete test application: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Summary
Write-Host ""
Write-Host "🎯 API TESTING SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

$testResults = @(
    @{ Name = "Health Check"; Success = ($healthResponse -ne $null) }
    @{ Name = "Root Endpoint"; Success = ($rootResponse -ne $null) }
    @{ Name = "Get Applications"; Success = ($applicationsResponse -ne $null) }
    @{ Name = "Create Application"; Success = ($createResponse -ne $null) }
    @{ Name = "Status Summary"; Success = ($statusSummaryResponse -ne $null) }
)

$successCount = ($testResults | Where-Object { $_.Success }).Count
$totalTests = $testResults.Count

Write-Host "Passed: $successCount / $totalTests tests" -ForegroundColor $(if ($successCount -eq $totalTests) { "Green" } else { "Yellow" })

foreach ($result in $testResults) {
    $status = if ($result.Success) { "✅" } else { "❌" }
    $color = if ($result.Success) { "Green" } else { "Red" }
    Write-Host "$status $($result.Name)" -ForegroundColor $color
}

Write-Host ""
Write-Host "📄 Your API Documentation: $ApiUrl/docs" -ForegroundColor Cyan
Write-Host "❤️ Health Check Endpoint: $ApiUrl/health" -ForegroundColor Cyan
Write-Host ""

if ($successCount -eq $totalTests) {
    Write-Host "🎉 All tests passed! Your API is ready for production." -ForegroundColor Green
} elseif ($successCount -gt 0) {
    Write-Host "⚠️ Some tests failed. Check the errors above and your deployment configuration." -ForegroundColor Yellow
} else {
    Write-Host "❌ All tests failed. Your API may not be properly deployed or accessible." -ForegroundColor Red
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Visit $ApiUrl/docs to see interactive API documentation" -ForegroundColor White
Write-Host "2. Update CORS settings for your production frontend" -ForegroundColor White
Write-Host "3. Configure monitoring and alerts in Render dashboard" -ForegroundColor White
Write-Host "4. Set up custom domain if needed" -ForegroundColor White

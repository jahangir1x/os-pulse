# Test script for sending events to the backend
$BackendUrl = "http://localhost:8080"

Write-Host "Testing Event Reception Endpoint" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: File Operation Event
Write-Host "Test 1: Sending file_operation event..." -ForegroundColor Yellow
$body1 = @{
    event_type = "file_operation"
    timestamp = "2025-10-28T16:10:50.269774Z"
    source = "os-pulse-controller"
    data = @{
        handle = "0x8e8"
        filePath = "\\?\C:\Users\rocky\AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations\f01b4d95cf55d32a.automaticDestinations-ms"
        bytesTransferred = 2
        content = "6F 01"
        timestamp = "2025-10-28T16:10:46.230Z"
        operation = "ReadFile"
        metadata = @{
            sessionId = "test-session-123"
            processName = "notepad.exe"
            processId = 9700
        }
    }
} | ConvertTo-Json -Depth 10

try {
    $response1 = Invoke-RestMethod -Uri "$BackendUrl/api/events" -Method Post -Body $body1 -ContentType "application/json"
    Write-Host "Response: $($response1 | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host ""

# Test 2: Process Creation Event
Write-Host "Test 2: Sending process_creation event..." -ForegroundColor Yellow
$body2 = @{
    event_type = "process_creation"
    timestamp = "2025-10-28T16:15:30.123456Z"
    source = "os-pulse-controller"
    data = @{
        processHandle = "0x1a4"
        threadHandle = "0x1a8"
        imagePath = "C:\Windows\System32\notepad.exe"
        commandLine = "notepad.exe test.txt"
        currentDirectory = "C:\Users\rocky\Desktop"
        status = 0
        operation = "NtCreateUserProcess"
        timestamp = "2025-10-28T16:15:30.100Z"
        metadata = @{
            sessionId = "test-session-456"
            processName = "explorer.exe"
            processId = 1234
        }
    }
} | ConvertTo-Json -Depth 10

try {
    $response2 = Invoke-RestMethod -Uri "$BackendUrl/api/events" -Method Post -Body $body2 -ContentType "application/json"
    Write-Host "Response: $($response2 | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host ""

# Test 3: Write Operation Event
Write-Host "Test 3: Sending WriteFile event..." -ForegroundColor Yellow
$body3 = @{
    event_type = "file_operation"
    timestamp = "2025-10-28T16:20:15.987654Z"
    source = "os-pulse-controller"
    data = @{
        handle = "0x2f4"
        filePath = "C:\Users\rocky\Desktop\test.txt"
        bytesTransferred = 13
        content = "48 65 6C 6C 6F 20 57 6F 72 6C 64 21 0A"
        timestamp = "2025-10-28T16:20:15.950Z"
        operation = "WriteFile"
        metadata = @{
            sessionId = "test-session-789"
            processName = "notepad.exe"
            processId = 5678
        }
    }
} | ConvertTo-Json -Depth 10

try {
    $response3 = Invoke-RestMethod -Uri "$BackendUrl/api/events" -Method Post -Body $body3 -ContentType "application/json"
    Write-Host "Response: $($response3 | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host ""

# Test 4: Event without sessionId
Write-Host "Test 4: Sending event without sessionId..." -ForegroundColor Yellow
$body4 = @{
    event_type = "registry_operation"
    timestamp = "2025-10-28T16:25:00.000000Z"
    source = "os-pulse-controller"
    data = @{
        operation = "RegSetValue"
        keyPath = "HKEY_CURRENT_USER\Software\TestApp"
        valueName = "TestValue"
        valueData = "TestData"
        timestamp = "2025-10-28T16:25:00.000Z"
    }
} | ConvertTo-Json -Depth 10

try {
    $response4 = Invoke-RestMethod -Uri "$BackendUrl/api/events" -Method Post -Body $body4 -ContentType "application/json"
    Write-Host "Response: $($response4 | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "Tests completed!" -ForegroundColor Cyan

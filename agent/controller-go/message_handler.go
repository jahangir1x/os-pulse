package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/fatih/color"
)

type MessageHandler struct {
	sessionInfo map[string]interface{}
	eventCount  int
	apiEnabled  bool
	apiEndpoint string
	apiKey      string
	httpClient  *http.Client
}

type Event struct {
	Type      string                 `json:"type"`
	Operation string                 `json:"operation,omitempty"`
	Data      map[string]interface{} `json:"data"`
	Metadata  map[string]interface{} `json:"metadata,omitempty"`
}

type APIPayload struct {
	EventType string                 `json:"event_type"`
	Timestamp string                 `json:"timestamp"`
	Source    string                 `json:"source"`
	Data      map[string]interface{} `json:"data"`
}

func NewMessageHandler() *MessageHandler {
	return &MessageHandler{
		sessionInfo: make(map[string]interface{}),
		eventCount:  0,
		apiEnabled:  false,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

func (mh *MessageHandler) EnableAPI(endpoint, apiKey string) {
	mh.apiEnabled = true
	mh.apiEndpoint = endpoint
	mh.apiKey = apiKey

	cyan := color.New(color.FgCyan)
	cyan.Printf("[HANDLER] API integration enabled - Endpoint: %s\n", endpoint)
}

func (mh *MessageHandler) HandleMessage(message json.RawMessage, data []byte) {
	var event Event
	if err := json.Unmarshal(message, &event); err != nil {
		red := color.New(color.FgRed)
		red.Printf("[ERROR] Failed to parse message: %v\n", err)
		return
	}

	mh.eventCount++

	// Route to appropriate handler
	switch event.Type {
	case "session_start":
		mh.handleSessionStart(event)
	case "file_operation":
		mh.handleFileOperation(event)
	case "process_creation":
		mh.handleProcessCreation(event)
	case "pong":
		mh.handlePong(event)
	case "status_response":
		mh.handleStatusResponse(event)
	default:
		yellow := color.New(color.FgYellow)
		yellow.Printf("[UNKNOWN] %s\n", string(message))
	}

	// Send to API immediately if enabled
	if mh.apiEnabled {
		go mh.sendToAPI(event)
	}
}

func (mh *MessageHandler) handleSessionStart(event Event) {
	green := color.New(color.FgGreen, color.Bold)
	cyan := color.New(color.FgCyan)

	green.Println("🚀 SESSION STARTED")

	if sessionId, ok := event.Data["sessionId"].(string); ok {
		mh.sessionInfo["sessionId"] = sessionId
		cyan.Printf("   Session ID: %s\n", sessionId)
	}

	if processName, ok := event.Data["processName"].(string); ok {
		mh.sessionInfo["processName"] = processName
		cyan.Printf("   Process: %s\n", processName)
	}

	if processId, ok := event.Data["processId"]; ok {
		mh.sessionInfo["processId"] = processId
		cyan.Printf("   PID: %v\n", processId)
	}

	if timestamp, ok := event.Data["timestamp"].(string); ok {
		cyan.Printf("   Started: %s\n", timestamp)
	}

	fmt.Println()
}

func (mh *MessageHandler) handleFileOperation(event Event) {
	blue := color.New(color.FgBlue, color.Bold)
	white := color.New(color.FgWhite)
	yellow := color.New(color.FgYellow)

	operation := event.Operation
	if operation == "" {
		operation = "Unknown"
	}

	blue.Printf("📁 FILE %s\n", operation)

	if filePath, ok := event.Data["filePath"].(string); ok {
		white.Printf("   Path: %s\n", filePath)
	}

	if bytes, ok := event.Data["bytesTransferred"]; ok {
		white.Printf("   Bytes: %v\n", bytes)
	}

	if content, ok := event.Data["content"].(string); ok && content != "" {
		if len(content) > 100 {
			content = content[:100] + "..."
		}
		yellow.Printf("   Content: %s\n", content)
	}

	if timestamp, ok := event.Data["timestamp"].(string); ok {
		white.Printf("   Time: %s\n", timestamp)
	}

	fmt.Println()
}

func (mh *MessageHandler) handleProcessCreation(event Event) {
	magenta := color.New(color.FgMagenta, color.Bold)
	white := color.New(color.FgWhite)

	operation := event.Operation
	if operation == "" {
		operation = "Unknown"
	}

	magenta.Printf("⚡ PROCESS %s\n", operation)

	if imagePath, ok := event.Data["imagePath"].(string); ok {
		white.Printf("   Image: %s\n", imagePath)
	}

	if commandLine, ok := event.Data["commandLine"].(string); ok {
		white.Printf("   Command: %s\n", commandLine)
	}

	if processHandle, ok := event.Data["processHandle"]; ok {
		white.Printf("   Handle: %v\n", processHandle)
	}

	if status, ok := event.Data["status"]; ok {
		white.Printf("   Status: %v\n", status)
	}

	if timestamp, ok := event.Data["timestamp"].(string); ok {
		white.Printf("   Time: %s\n", timestamp)
	}

	fmt.Println()
}

func (mh *MessageHandler) handlePong(event Event) {
	green := color.New(color.FgGreen)
	green.Println("🏓 PONG received from injector")

	if timestamp, ok := event.Data["timestamp"].(string); ok {
		fmt.Printf("   Timestamp: %s\n", timestamp)
	}
	fmt.Println()
}

func (mh *MessageHandler) handleStatusResponse(event Event) {
	cyan := color.New(color.FgCyan)
	white := color.New(color.FgWhite)

	cyan.Println("📊 STATUS RESPONSE")

	if sessionId, ok := event.Data["sessionId"].(string); ok {
		white.Printf("   Session: %s\n", sessionId)
	}

	if processName, ok := event.Data["processName"].(string); ok {
		white.Printf("   Process: %s\n", processName)
	}

	if processId, ok := event.Data["processId"]; ok {
		white.Printf("   PID: %v\n", processId)
	}

	if status, ok := event.Data["status"].(string); ok {
		white.Printf("   Status: %s\n", status)
	}

	fmt.Println()
}

func (mh *MessageHandler) sendToAPI(event Event) {
	if !mh.apiEnabled || mh.apiEndpoint == "" {
		return
	}

	// Create API payload
	payload := APIPayload{
		EventType: event.Type,
		Timestamp: time.Now().UTC().Format(time.RFC3339),
		Source:    "os-pulse-controller-go",
		Data:      event.Data,
	}

	// Marshal to JSON
	jsonData, err := json.Marshal(payload)
	if err != nil {
		red := color.New(color.FgRed)
		red.Printf("[API] Failed to marshal event: %v\n", err)
		return
	}

	// Create request
	req, err := http.NewRequest("POST", mh.apiEndpoint+"/events", bytes.NewBuffer(jsonData))
	if err != nil {
		red := color.New(color.FgRed)
		red.Printf("[API] Failed to create request: %v\n", err)
		return
	}

	// Set headers
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("User-Agent", "OS-Pulse-Controller-Go/1.0")

	if mh.apiKey != "" {
		req.Header.Set("Authorization", "Bearer "+mh.apiKey)
	}

	// Send request
	resp, err := mh.httpClient.Do(req)
	if err != nil {
		yellow := color.New(color.FgYellow)
		yellow.Printf("[API] Request failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	// Check response
	if resp.StatusCode == 200 {
		green := color.New(color.FgGreen)
		green.Printf("[API] Event sent successfully (%s)\n", event.Type)
	} else {
		yellow := color.New(color.FgYellow)
		yellow.Printf("[API] Unexpected status %d - dropping event (%s)\n", resp.StatusCode, event.Type)
	}
}

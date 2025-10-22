package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"os/signal"
	"path/filepath"
	"syscall"

	"github.com/fatih/color"
	"github.com/frida/frida-go/frida"
)

type FridaController struct {
	deviceManager  *frida.DeviceManager
	session        *frida.Session
	script         *frida.Script
	agentCode      string
	messageHandler *MessageHandler
	running        bool
}

func NewFridaController() *FridaController {
	// Find and load agent script
	agentPath := findAgentScript()
	agentCode, err := loadAgentScript(agentPath)
	if err != nil {
		log.Fatalf("Failed to load agent script: %v", err)
	}

	green := color.New(color.FgGreen)
	green.Printf("[CONTROLLER] Initialized with agent script: %s\n", agentPath)

	return &FridaController{
		agentCode:      agentCode,
		messageHandler: NewMessageHandler(),
		running:        false,
	}
}

func (fc *FridaController) EnableAPI(endpoint, apiKey string) {
	fc.messageHandler.EnableAPI(endpoint, apiKey)
}

func findAgentScript() string {
	// Look for _agent.js in the injector folder
	scriptPath := filepath.Join("..", "injector", "_agent.js")

	if _, err := os.Stat(scriptPath); os.IsNotExist(err) {
		log.Fatalf("Agent script not found at %s", scriptPath)
	}

	return scriptPath
}

func loadAgentScript(path string) (string, error) {
	content, err := ioutil.ReadFile(path)
	if err != nil {
		return "", err
	}
	return string(content), nil
}

func (fc *FridaController) ListProcesses(filter string) {
	deviceManager := frida.NewDeviceManager()
	device, err := deviceManager.LocalDevice()
	if err != nil {
		red := color.New(color.FgRed)
		red.Printf("[ERROR] Failed to get local device: %v\n", err)
		return
	}

	processes, err := device.EnumerateProcesses(frida.ScopeFull)
	if err != nil {
		red := color.New(color.FgRed)
		red.Printf("[ERROR] Failed to enumerate processes: %v\n", err)
		return
	}

	green := color.New(color.FgGreen)
	white := color.New(color.FgWhite)
	cyan := color.New(color.FgCyan)

	fmt.Println()
	green.Println("Running Processes:")
	white.Printf("%-8s %-20s %-50s\n", "PID", "Name", "Path")
	white.Println("--------------------------------------------------------------------------------")

	count := 0
	for _, proc := range processes {
		name := proc.Name()
		if filter == "" || contains(name, filter) {
			pid := proc.PID()
			// Note: frida.Process doesn't have direct access to executable path
			// We'll just show what we have
			cyan.Printf("%-8d %-20s %-50s\n", pid, truncate(name, 19), "N/A")
			count++
			if count >= 20 {
				break
			}
		}
	}

	if count >= 20 {
		yellow := color.New(color.FgYellow)
		yellow.Printf("... and more processes (showing first 20)\n")
	}
}

func (fc *FridaController) SpawnProcess(executable string) {
	yellow := color.New(color.FgYellow)
	yellow.Printf("[SPAWN] Starting process: %s\n", executable)

	deviceManager := frida.NewDeviceManager()
	device, err := deviceManager.LocalDevice()
	if err != nil {
		red := color.New(color.FgRed)
		red.Printf("[ERROR] Failed to get local device: %v\n", err)
		return
	}

	// Spawn the process
	pid, err := device.Spawn(executable, frida.NewSpawnOptions())
	if err != nil {
		red := color.New(color.FgRed)
		red.Printf("[ERROR] Failed to spawn process: %v\n", err)
		return
	}

	green := color.New(color.FgGreen)
	green.Printf("[SPAWN] Process spawned with PID: %d\n", pid)

	// Attach to the spawned process
	fc.attachToProcess(device, pid)

	// Resume the process
	device.Resume(pid)

	// Wait for termination
	fc.waitForTermination()
}

func (fc *FridaController) AttachToProcessByName(processName string) {
	yellow := color.New(color.FgYellow)
	yellow.Printf("[ATTACH] Attaching to process: %s\n", processName)

	deviceManager := frida.NewDeviceManager()
	device, err := deviceManager.LocalDevice()
	if err != nil {
		red := color.New(color.FgRed)
		red.Printf("[ERROR] Failed to get local device: %v\n", err)
		return
	}

	// Find process by name
	processes, err := device.EnumerateProcesses(frida.ScopeFull)
	if err != nil {
		red := color.New(color.FgRed)
		red.Printf("[ERROR] Failed to enumerate processes: %v\n", err)
		return
	}

	var targetPID int = 0
	for _, proc := range processes {
		if proc.Name() == processName {
			targetPID = proc.PID()
			break
		}
	}

	if targetPID == 0 {
		red := color.New(color.FgRed)
		red.Printf("[ERROR] Process '%s' not found\n", processName)
		return
	}

	fc.attachToProcess(device, targetPID)
	fc.waitForTermination()
}

func (fc *FridaController) AttachToProcessByPID(pid int) {
	yellow := color.New(color.FgYellow)
	yellow.Printf("[ATTACH] Attaching to PID: %d\n", pid)

	deviceManager := frida.NewDeviceManager()
	device, err := deviceManager.LocalDevice()
	if err != nil {
		red := color.New(color.FgRed)
		red.Printf("[ERROR] Failed to get local device: %v\n", err)
		return
	}

	fc.attachToProcess(device, pid)
	fc.waitForTermination()
}

func (fc *FridaController) attachToProcess(device frida.DeviceInt, pid int) {
	session, err := device.Attach(pid, &frida.SessionOptions{})
	if err != nil {
		red := color.New(color.FgRed)
		red.Printf("[ERROR] Failed to attach to process: %v\n", err)
		return
	}

	fc.session = session
	green := color.New(color.FgGreen)
	green.Printf("[ATTACH] Successfully attached to PID: %d\n", pid)

	// Create and load script
	script, err := session.CreateScript(fc.agentCode)
	if err != nil {
		red := color.New(color.FgRed)
		red.Printf("[ERROR] Failed to create script: %v\n", err)
		return
	}

	fc.script = script

	// Set up message handler
	script.On("message", func(message json.RawMessage, data []byte) {
		fc.messageHandler.HandleMessage(message, data)
	})

	// Load the script
	err = script.Load()
	if err != nil {
		red := color.New(color.FgRed)
		red.Printf("[ERROR] Failed to load script: %v\n", err)
		return
	}

	fc.running = true
	green.Println("[SCRIPT] Agent loaded and running")
	cyan := color.New(color.FgCyan)
	cyan.Println("[INFO] Monitoring started. Press Ctrl+C to stop.")
}

func (fc *FridaController) waitForTermination() {
	// Set up signal handling
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	// Wait for signal
	<-sigChan

	yellow := color.New(color.FgYellow)
	yellow.Println("\n[SHUTDOWN] Shutting down gracefully...")

	fc.cleanup()
}

func (fc *FridaController) cleanup() {
	fc.running = false

	if fc.script != nil {
		fc.script.Unload()
		fc.script = nil
	}

	if fc.session != nil {
		fc.session.Detach()
		fc.session = nil
	}

	green := color.New(color.FgGreen)
	green.Println("[SHUTDOWN] Cleanup completed")
}

// Utility functions
func contains(str, substr string) bool {
	return len(substr) == 0 || len(str) >= len(substr) && str[:len(substr)] == substr
}

func truncate(str string, length int) string {
	if len(str) <= length {
		return str
	}
	return str[:length]
}

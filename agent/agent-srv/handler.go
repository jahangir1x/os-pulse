package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"

	"github.com/labstack/echo/v4"
)

type Handler struct {
	desktopPath    string
	controllerPath string
	monitoringCmd  *exec.Cmd
}

func NewHandler() *Handler {
	// Get user's Desktop path
	homeDir, err := os.UserHomeDir()
	if err != nil {
		log.Fatal("Failed to get user home directory:", err)
	}

	desktopPath := filepath.Join(homeDir, "Desktop")
	if runtime.GOOS == "windows" {
		desktopPath = filepath.Join(homeDir, "Desktop")
	}

	// Get controller path (relative to agent-srv)
	controllerPath := filepath.Join("..", "controller", "main.py")

	return &Handler{
		desktopPath:    desktopPath,
		controllerPath: controllerPath,
	}
}

// UploadFileRequest represents the file upload request
type UploadFileRequest struct {
	FileName string `json:"fileName"`
}

// StartMonitorRequest represents the start monitoring request
type StartMonitorRequest struct {
	SessionID string `json:"sessionId"`
	FileName  string `json:"fileName"`
	Mode      int    `json:"mode"`
	Processes []int  `json:"processes,omitempty"`
}

// StopMonitorRequest represents the stop monitoring request
type StopMonitorRequest struct {
	SessionID string `json:"sessionId"`
}

// ProcessInfo represents a running process
type ProcessInfo struct {
	PID  int    `json:"pid"`
	Name string `json:"name"`
}

// UploadFile handles file uploads and saves them to Desktop
func (h *Handler) UploadFile(c echo.Context) error {
	// Get uploaded file
	file, err := c.FormFile("file")
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Failed to get uploaded file: " + err.Error(),
		})
	}

	// Open uploaded file
	src, err := file.Open()
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Failed to open uploaded file: " + err.Error(),
		})
	}
	defer src.Close()

	// Create destination file on Desktop
	dstPath := filepath.Join(h.desktopPath, file.Filename)
	dst, err := os.Create(dstPath)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Failed to create file on Desktop: " + err.Error(),
		})
	}
	defer dst.Close()

	// Copy file content
	if _, err = io.Copy(dst, src); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Failed to copy file content: " + err.Error(),
		})
	}

	log.Printf("File uploaded successfully: %s", dstPath)

	return c.JSON(http.StatusOK, map[string]string{
		"message": "File uploaded successfully",
		"path":    dstPath,
	})
}

// ListProcesses returns running processes using tasklist
func (h *Handler) ListProcesses(c echo.Context) error {
	var cmd *exec.Cmd

	if runtime.GOOS == "windows" {
		// Use tasklist on Windows
		cmd = exec.Command("tasklist", "/FO", "CSV", "/NH")
	} else {
		// Use ps on Unix-like systems
		cmd = exec.Command("ps", "aux")
	}

	output, err := cmd.Output()
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Failed to get process list: " + err.Error(),
		})
	}

	// Parse tasklist output
	processes := h.parseTaskList(string(output))

	return c.JSON(http.StatusOK, processes)
}

// parseTaskList parses Windows tasklist CSV output
func (h *Handler) parseTaskList(output string) []ProcessInfo {
	var processes []ProcessInfo
	lines := strings.Split(output, "\n")

	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}

		// Parse CSV format: "name","pid","session","mem","status"
		parts := strings.Split(line, ",")
		if len(parts) < 2 {
			continue
		}

		// Remove quotes
		name := strings.Trim(parts[0], "\"")
		pidStr := strings.Trim(parts[1], "\"")

		// Parse PID
		var pid int
		fmt.Sscanf(pidStr, "%d", &pid)

		processes = append(processes, ProcessInfo{
			PID:  pid,
			Name: name,
		})
	}

	return processes
}

// StartMonitor handles start monitoring requests
func (h *Handler) StartMonitor(c echo.Context) error {
	var req StartMonitorRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body: " + err.Error(),
		})
	}

	// Build command based on mode
	var cmd *exec.Cmd
	pythonPath := "python"

	switch req.Mode {
	case 1: // All Processes
		if req.FileName != "" {
			// Attach to all processes with filter
			cmd = exec.Command(pythonPath, h.controllerPath, "attach", "--all", "--filter", req.FileName)
		} else {
			cmd = exec.Command(pythonPath, h.controllerPath, "attach", "--all")
		}

	case 2: // Specific Processes
		if len(req.Processes) > 0 {
			// Attach to specific PIDs
			args := []string{h.controllerPath, "attach", "--pids"}
			for _, pid := range req.Processes {
				args = append(args, fmt.Sprintf("%d", pid))
			}
			cmd = exec.Command(pythonPath, args...)
		} else {
			return c.JSON(http.StatusBadRequest, map[string]string{
				"error": "Mode 2 requires process list",
			})
		}

	case 3: // Spawn Uploaded
		if req.FileName == "" {
			return c.JSON(http.StatusBadRequest, map[string]string{
				"error": "Mode 3 requires fileName",
			})
		}
		// Spawn the uploaded file
		// execPath := filepath.Join(h.desktopPath, req.FileName)
		// cmd = exec.Command(pythonPath, h.controllerPath, "spawn", "--executable", execPath)
		cmd = exec.Command(pythonPath, h.controllerPath, "spawn", "--executable", "C:\\Windows\\System32\\Notepad.exe") // For testing purposes

	default:
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid monitoring mode",
		})
	}

	// Set environment variables
	cmd.Env = append(os.Environ(), fmt.Sprintf("SESSION_ID=%s", req.SessionID))

	// Start the monitoring process in background
	if err := cmd.Start(); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{
			"error": "Failed to start monitoring: " + err.Error(),
		})
	}

	// Store the command for later termination
	h.monitoringCmd = cmd

	log.Printf("Started monitoring with PID: %d, SessionID: %s, Mode: %d",
		cmd.Process.Pid, req.SessionID, req.Mode)

	return c.JSON(http.StatusOK, map[string]interface{}{
		"message":       "Monitoring started successfully",
		"sessionId":     req.SessionID,
		"monitoringPid": cmd.Process.Pid,
	})
}

// StopMonitor handles stop monitoring requests
func (h *Handler) StopMonitor(c echo.Context) error {
	var req StopMonitorRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{
			"error": "Invalid request body: " + err.Error(),
		})
	}

	// Kill all Python processes (as specified)
	var cmd *exec.Cmd
	if runtime.GOOS == "windows" {
		cmd = exec.Command("taskkill", "/F", "/IM", "python.exe")
	} else {
		cmd = exec.Command("pkill", "-9", "python")
	}

	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Printf("Warning: Failed to kill python processes: %v, output: %s", err, string(output))
		// Don't return error, as processes might already be stopped
	}

	// Also try to kill the stored monitoring command if exists
	if h.monitoringCmd != nil && h.monitoringCmd.Process != nil {
		h.monitoringCmd.Process.Kill()
		h.monitoringCmd = nil
	}

	log.Printf("Stopped monitoring for session: %s", req.SessionID)

	return c.JSON(http.StatusOK, map[string]string{
		"message": "Monitoring stopped successfully",
	})
}

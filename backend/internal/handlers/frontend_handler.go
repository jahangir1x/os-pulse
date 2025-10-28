package handlers

import (
	"io"
	"net/http"
	"strconv"

	"os-pulse-backend/internal/models"
	"os-pulse-backend/internal/service"

	"github.com/labstack/echo/v4"
)

type FrontendHandler struct {
	eventService   *service.EventService
	sessionService *service.SessionService
}

func NewFrontendHandler(eventService *service.EventService, sessionService *service.SessionService) *FrontendHandler {
	return &FrontendHandler{
		eventService:   eventService,
		sessionService: sessionService,
	}
}

func (h *FrontendHandler) CreateSession(c echo.Context) error {
	// Get file from form data
	file, err := c.FormFile("file")
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "No file provided"})
	}

	// Open file
	src, err := file.Open()
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to open file"})
	}
	defer src.Close()

	// Read file content
	fileContent, err := io.ReadAll(src)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to read file"})
	}

	// Create session
	response, err := h.sessionService.CreateSession(file.Filename, fileContent)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to create session"})
	}

	return c.JSON(http.StatusOK, response)
}

func (h *FrontendHandler) GetMonitorModes(c echo.Context) error {
	modes := h.sessionService.GetMonitorModes()
	return c.JSON(http.StatusOK, modes)
}

func (h *FrontendHandler) StartMonitor(c echo.Context) error {
	var req models.StartMonitorRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body"})
	}

	if err := h.eventService.StartMonitoring(&req); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to start monitoring"})
	}

	return c.JSON(http.StatusOK, models.MessageResponse{Message: "monitoring started successfully"})
}

func (h *FrontendHandler) StopMonitor(c echo.Context) error {
	var req models.StopMonitorRequest
	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body"})
	}

	if err := h.eventService.StopMonitoring(&req); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to stop monitoring"})
	}

	return c.JSON(http.StatusOK, models.MessageResponse{Message: "monitoring stopped successfully"})
}

func (h *FrontendHandler) GetEvents(c echo.Context) error {
	// Get limit from query parameter (default 10)
	limit := 10
	if limitStr := c.QueryParam("limit"); limitStr != "" {
		if parsedLimit, err := strconv.Atoi(limitStr); err == nil && parsedLimit > 0 {
			limit = parsedLimit
		}
	}

	// Get unsent events in batch
	events, err := h.eventService.GetUnsentEvents(limit)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to get events"})
	}

	// Convert events to frontend format
	frontendEvents := make([]map[string]interface{}, len(events))
	for i, event := range events {
		frontendEvents[i] = map[string]interface{}{
			"id":         event.ID,
			"event_type": event.EventType,
			"timestamp":  event.Timestamp,
			"source":     event.Source,
			"data":       event.Data,
			"session_id": event.SessionID,
		}
	}

	return c.JSON(http.StatusOK, frontendEvents)
}

func (h *FrontendHandler) ListProcesses(c echo.Context) error {
	var req struct {
		SessionID string `json:"sessionId"`
	}

	if err := c.Bind(&req); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body"})
	}

	processes, err := h.sessionService.GetRunningProcesses(req.SessionID)
	if err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to get processes"})
	}

	return c.JSON(http.StatusOK, processes)
}

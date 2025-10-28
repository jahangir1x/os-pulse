package handlers

import (
	"net/http"
	"time"

	"os-pulse-backend/internal/models"
	"os-pulse-backend/internal/service"

	"github.com/labstack/echo/v4"
	"gorm.io/datatypes"
)

type EventHandler struct {
	eventService *service.EventService
}

func NewEventHandler(eventService *service.EventService) *EventHandler {
	return &EventHandler{
		eventService: eventService,
	}
}

func (h *EventHandler) ReceiveEvent(c echo.Context) error {
	var rawEvent map[string]interface{}
	if err := c.Bind(&rawEvent); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body"})
	}

	// Extract basic fields
	eventType, _ := rawEvent["event_type"].(string)
	source, _ := rawEvent["source"].(string)
	timestampStr, _ := rawEvent["timestamp"].(string)

	// Parse timestamp
	timestamp, err := time.Parse(time.RFC3339, timestampStr)
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid timestamp format"})
	}

	// Extract session ID from event data if available
	var sessionID string
	if data, ok := rawEvent["data"].(map[string]interface{}); ok {
		if metadata, ok := data["metadata"].(map[string]interface{}); ok {
			if sid, ok := metadata["sessionId"].(string); ok {
				sessionID = sid
			}
		}
	}

	// Convert data to JSONB
	eventData := datatypes.JSON{}
	if err := eventData.Scan(rawEvent["data"]); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Failed to process event data"})
	}

	event := &models.Event{
		SessionID: sessionID,
		EventType: eventType,
		Timestamp: timestamp,
		Source:    source,
		Data:      eventData,
		IsSent:    false,
	}

	if err := h.eventService.CreateEvent(event); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to create event"})
	}

	return c.JSON(http.StatusOK, map[string]string{"status": "success"})
}

func (h *EventHandler) ReceiveHTTPEvent(c echo.Context) error {
	var httpEvent models.HTTPEvent
	if err := c.Bind(&httpEvent); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body"})
	}

	// For HTTP events, we need to determine the session ID
	// For now, we'll use a default session or extract from context
	sessionID := c.QueryParam("sessionId")
	if sessionID == "" {
		// Could extract from request headers or use a default
		sessionID = "default-session"
	}

	if err := h.eventService.CreateHTTPEvent(sessionID, &httpEvent); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to create HTTP event"})
	}

	return c.JSON(http.StatusOK, map[string]string{"status": "success"})
}

func (h *EventHandler) ReceiveNetEvent(c echo.Context) error {
	var networkEvent models.NetworkEvent
	if err := c.Bind(&networkEvent); err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid request body"})
	}

	// For network events, we need to determine the session ID
	sessionID := c.QueryParam("sessionId")
	if sessionID == "" {
		sessionID = "default-session"
	}

	if err := h.eventService.CreateNetworkEvents(sessionID, &networkEvent); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to create network events"})
	}

	return c.JSON(http.StatusOK, map[string]string{"status": "success"})
}

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
		// Try alternative timestamp format
		timestamp, err = time.Parse(time.RFC3339Nano, timestampStr)
		if err != nil {
			return c.JSON(http.StatusBadRequest, map[string]string{"error": "Invalid timestamp format"})
		}
	}

	// Extract session ID from event data metadata (optional)
	var sessionID string
	if data, ok := rawEvent["data"].(map[string]interface{}); ok {
		if metadata, ok := data["metadata"].(map[string]interface{}); ok {
			if sid, ok := metadata["sessionId"].(string); ok {
				sessionID = sid
			}
		}
	}

	// Convert entire data object to JSONB
	dataBytes, err := datatypes.NewJSONType(rawEvent["data"]).MarshalJSON()
	if err != nil {
		return c.JSON(http.StatusBadRequest, map[string]string{"error": "Failed to marshal event data"})
	}

	eventData := datatypes.JSON(dataBytes)

	// Create event (sessionID is optional, can be empty string)
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

	// Session ID is optional - can be from query param or empty
	sessionID := c.QueryParam("sessionId")

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

	// Session ID is optional - can be from query param or empty
	sessionID := c.QueryParam("sessionId")

	if err := h.eventService.CreateNetworkEvents(sessionID, &networkEvent); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": "Failed to create network events"})
	}

	return c.JSON(http.StatusOK, map[string]string{"status": "success"})
}

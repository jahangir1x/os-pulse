package repository

import (
	"fmt"
	"os-pulse-backend/internal/models"
	"time"

	"gorm.io/datatypes"
	"gorm.io/gorm"
)

type EventRepository struct {
	db *gorm.DB
}

func NewEventRepository(db *gorm.DB) *EventRepository {
	return &EventRepository{db: db}
}

func (r *EventRepository) CreateEvent(event *models.Event) error {
	result := r.db.Create(event)
	if result.Error != nil {
		return fmt.Errorf("failed to create event: %w", result.Error)
	}
	return nil
}

// GetUnsentEvents retrieves unsent events in batches
func (r *EventRepository) GetUnsentEvents(limit int) ([]*models.Event, error) {
	var events []*models.Event

	result := r.db.Where("is_sent = ?", false).
		Order("timestamp ASC").
		Limit(limit).
		Find(&events)

	if result.Error != nil {
		return nil, fmt.Errorf("failed to query events: %w", result.Error)
	}

	return events, nil
}

// GetEventsByTimeRange retrieves events within a time range
func (r *EventRepository) GetEventsByTimeRange(startTime, endTime time.Time, limit int) ([]*models.Event, error) {
	var events []*models.Event

	result := r.db.Where("timestamp BETWEEN ? AND ?", startTime, endTime).
		Order("timestamp ASC").
		Limit(limit).
		Find(&events)

	if result.Error != nil {
		return nil, fmt.Errorf("failed to query events: %w", result.Error)
	}

	return events, nil
}

// GetAllEvents retrieves all events with pagination
func (r *EventRepository) GetAllEvents(offset, limit int) ([]*models.Event, error) {
	var events []*models.Event

	result := r.db.Order("timestamp DESC").
		Offset(offset).
		Limit(limit).
		Find(&events)

	if result.Error != nil {
		return nil, fmt.Errorf("failed to query events: %w", result.Error)
	}

	return events, nil
}

func (r *EventRepository) MarkEventsAsSent(eventIDs []uint64) error {
	if len(eventIDs) == 0 {
		return nil
	}

	result := r.db.Model(&models.Event{}).Where("id IN ?", eventIDs).Update("is_sent", true)
	if result.Error != nil {
		return fmt.Errorf("failed to mark events as sent: %w", result.Error)
	}

	return nil
}

// CountUnsentEvents returns the total count of unsent events
func (r *EventRepository) CountUnsentEvents() (int64, error) {
	var count int64
	result := r.db.Model(&models.Event{}).Where("is_sent = ?", false).Count(&count)
	if result.Error != nil {
		return 0, fmt.Errorf("failed to count unsent events: %w", result.Error)
	}
	return count, nil
}

// CountAllEvents returns the total count of all events
func (r *EventRepository) CountAllEvents() (int64, error) {
	var count int64
	result := r.db.Model(&models.Event{}).Count(&count)
	if result.Error != nil {
		return 0, fmt.Errorf("failed to count events: %w", result.Error)
	}
	return count, nil
}

func (r *EventRepository) CreateHTTPEvent(sessionID string, httpEvent *models.HTTPEvent) error {
	// Convert HTTP event to JSON bytes first
	jsonBytes, err := datatypes.NewJSONType(httpEvent).MarshalJSON()
	if err != nil {
		return fmt.Errorf("failed to marshal HTTP event: %w", err)
	}

	eventData := datatypes.JSON(jsonBytes)

	event := &models.Event{
		SessionID: sessionID, // Optional, can be empty
		EventType: "http_network_operation",
		Timestamp: time.UnixMilli(httpEvent.TimestampMS),
		Source:    "http-interceptor",
		Data:      eventData,
		IsSent:    false,
	}

	return r.CreateEvent(event)
}

func (r *EventRepository) CreateNetworkEvents(sessionID string, networkEvent *models.NetworkEvent) error {
	// Create individual events for each network event
	for _, netEvent := range networkEvent.Events {
		// Convert network event to JSON bytes first
		jsonBytes, err := datatypes.NewJSONType(netEvent).MarshalJSON()
		if err != nil {
			return fmt.Errorf("failed to marshal network event: %w", err)
		}

		eventData := datatypes.JSON(jsonBytes)

		event := &models.Event{
			SessionID: sessionID, // Optional, can be empty
			EventType: "raw_network_operation",
			Timestamp: time.Unix(int64(netEvent.Timestamp), 0),
			Source:    "network-interceptor",
			Data:      eventData,
			IsSent:    false,
		}

		if err := r.CreateEvent(event); err != nil {
			return err
		}
	}

	return nil
}

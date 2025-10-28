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

func (r *EventRepository) GetUnsentEventsBySession(sessionID string, limit int) ([]*models.Event, error) {
	var events []*models.Event

	result := r.db.Where("session_id = ? AND is_sent = ?", sessionID, false).
		Order("timestamp DESC").
		Limit(limit).
		Find(&events)

	if result.Error != nil {
		return nil, fmt.Errorf("failed to query events: %w", result.Error)
	}

	return events, nil
}

func (r *EventRepository) GetEventsBySessionInTimeRange(sessionID string, startTime, endTime *time.Time, limit int) ([]*models.Event, error) {
	var events []*models.Event
	query := r.db.Where("session_id = ? AND is_sent = ?", sessionID, false)

	if startTime != nil && endTime != nil {
		query = query.Where("timestamp BETWEEN ? AND ?", startTime, endTime)
	} else if startTime != nil {
		query = query.Where("timestamp >= ?", startTime)
	}

	result := query.Order("timestamp DESC").Limit(limit).Find(&events)

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

func (r *EventRepository) CreateHTTPEvent(sessionID string, httpEvent *models.HTTPEvent) error {
	// Convert HTTP event to JSONB
	eventData := datatypes.JSON{}
	if err := eventData.Scan(httpEvent); err != nil {
		return fmt.Errorf("failed to marshal HTTP event: %w", err)
	}

	event := &models.Event{
		SessionID: sessionID,
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
		eventData := datatypes.JSON{}
		if err := eventData.Scan(netEvent); err != nil {
			return fmt.Errorf("failed to marshal network event: %w", err)
		}

		event := &models.Event{
			SessionID: sessionID,
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

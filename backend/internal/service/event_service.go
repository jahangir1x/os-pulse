package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"os-pulse-backend/internal/models"
	"os-pulse-backend/internal/repository"
)

type EventService struct {
	eventRepo       *repository.EventRepository
	sessionRepo     *repository.SessionRepository
	agentServiceURL string
}

func NewEventService(eventRepo *repository.EventRepository, sessionRepo *repository.SessionRepository, agentServiceURL string) *EventService {
	return &EventService{
		eventRepo:       eventRepo,
		sessionRepo:     sessionRepo,
		agentServiceURL: agentServiceURL,
	}
}

func (s *EventService) CreateEvent(event *models.Event) error {
	// Set default values
	if event.IsSent == false {
		event.IsSent = false
	}

	return s.eventRepo.CreateEvent(event)
}

func (s *EventService) GetEventsForSession(sessionID string, limit int) ([]*models.Event, error) {
	// Get session to check monitoring time range
	session, err := s.sessionRepo.GetSessionByID(sessionID)
	if err != nil {
		// If session doesn't exist, return empty events
		return []*models.Event{}, nil
	}

	// Get events in the monitoring time range
	events, err := s.eventRepo.GetEventsBySessionInTimeRange(
		sessionID,
		session.MonitoringStarted,
		session.MonitoringEnded,
		limit,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to get events: %w", err)
	}

	// Mark events as sent if any were returned
	if len(events) > 0 {
		eventIDs := make([]uint64, len(events))
		for i, event := range events {
			eventIDs[i] = event.ID
		}

		if err := s.eventRepo.MarkEventsAsSent(eventIDs); err != nil {
			// Log error but don't fail the request
			fmt.Printf("Warning: failed to mark events as sent: %v\n", err)
		}
	}

	return events, nil
}

func (s *EventService) CreateHTTPEvent(sessionID string, httpEvent *models.HTTPEvent) error {
	return s.eventRepo.CreateHTTPEvent(sessionID, httpEvent)
}

func (s *EventService) CreateNetworkEvents(sessionID string, networkEvent *models.NetworkEvent) error {
	return s.eventRepo.CreateNetworkEvents(sessionID, networkEvent)
}

func (s *EventService) StartMonitoring(req *models.StartMonitorRequest) error {
	// Update session monitoring started time
	err := s.sessionRepo.UpdateSessionMonitoringStarted(req.SessionID, time.Now())
	if err != nil {
		return fmt.Errorf("failed to update session: %w", err)
	}

	// Forward request to agent service
	return s.forwardStartMonitorRequest(req)
}

func (s *EventService) StopMonitoring(req *models.StopMonitorRequest) error {
	// Update session monitoring ended time
	err := s.sessionRepo.UpdateSessionMonitoringEnded(req.SessionID, time.Now())
	if err != nil {
		return fmt.Errorf("failed to update session: %w", err)
	}

	// Forward request to agent service
	return s.forwardStopMonitorRequest(req)
}

func (s *EventService) forwardStartMonitorRequest(req *models.StartMonitorRequest) error {
	// Fetch the session to get the file name
	session, err := s.sessionRepo.GetSessionByID(req.SessionID)
	if err != nil {
		return fmt.Errorf("failed to get session: %w", err)
	}

	// Add file name to the request
	req.FileName = session.FileName

	jsonData, err := json.Marshal(req)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	resp, err := http.Post(
		s.agentServiceURL+"/api/start-monitor",
		"application/json",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return fmt.Errorf("failed to forward start monitor request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("agent service returned error: %s", string(body))
	}

	return nil
}

func (s *EventService) forwardStopMonitorRequest(req *models.StopMonitorRequest) error {
	jsonData, err := json.Marshal(req)
	if err != nil {
		return fmt.Errorf("failed to marshal request: %w", err)
	}

	resp, err := http.Post(
		s.agentServiceURL+"/api/stop-monitor",
		"application/json",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return fmt.Errorf("failed to forward stop monitor request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("agent service returned error: %s", string(body))
	}

	return nil
}

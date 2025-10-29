package service

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"sort"
	"strings"
	"time"

	"os-pulse-backend/internal/models"
	"os-pulse-backend/internal/repository"

	"github.com/google/uuid"
)

type SessionService struct {
	sessionRepo     *repository.SessionRepository
	agentServiceURL string
}

func NewSessionService(sessionRepo *repository.SessionRepository, agentServiceURL string) *SessionService {
	return &SessionService{
		sessionRepo:     sessionRepo,
		agentServiceURL: agentServiceURL,
	}
}

func (s *SessionService) CreateSession(fileName string, fileContent []byte) (*models.CreateSessionResponse, error) {
	// Generate session ID
	sessionID := uuid.New().String()

	// Create session in database
	session := &models.Session{
		ID:        sessionID,
		FileName:  fileName,
		CreatedAt: time.Now(),
		IsActive:  false,
	}

	err := s.sessionRepo.CreateSession(session)
	if err != nil {
		return nil, fmt.Errorf("failed to create session: %w", err)
	}

	// Forward file to agent service
	err = s.uploadFileToAgent(fileName, fileContent)
	if err != nil {
		return nil, fmt.Errorf("failed to upload file to agent: %w", err)
	}

	return &models.CreateSessionResponse{
		SessionID: sessionID,
	}, nil
}

func (s *SessionService) GetSession(sessionID string) (*models.Session, error) {
	return s.sessionRepo.GetSessionByID(sessionID)
}

func (s *SessionService) GetActiveSessions() ([]*models.Session, error) {
	return s.sessionRepo.GetActiveSessions()
}

func (s *SessionService) uploadFileToAgent(fileName string, fileContent []byte) error {
	// Create multipart form
	var buf bytes.Buffer
	writer := multipart.NewWriter(&buf)

	// Add file part
	part, err := writer.CreateFormFile("file", fileName)
	if err != nil {
		return fmt.Errorf("failed to create form file: %w", err)
	}

	_, err = part.Write(fileContent)
	if err != nil {
		return fmt.Errorf("failed to write file content: %w", err)
	}

	err = writer.Close()
	if err != nil {
		return fmt.Errorf("failed to close writer: %w", err)
	}

	// Send request to agent service
	req, err := http.NewRequest("POST", s.agentServiceURL+"/api/upload-file", &buf)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{
		Timeout: 30 * time.Second,
	}

	resp, err := client.Do(req)
	if err != nil {
		return fmt.Errorf("failed to send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("agent service returned error: %s", string(body))
	}

	return nil
}

func (s *SessionService) GetMonitorModes() []*models.MonitorMode {
	return []*models.MonitorMode{
		// {ID: 1, Mode: "All Processes"},
		{ID: 2, Mode: "Specific Processes"},
		// {ID: 3, Mode: "Spawn Uploaded"},
	}
}

func (s *SessionService) GetRunningProcesses(sessionID string) ([]*models.RunningProcess, error) {
	// Call agent service to get running processes
	resp, err := http.Post(
		s.agentServiceURL+"/api/list-processes",
		"application/json",
		bytes.NewBuffer([]byte("{}")),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to call agent service: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("agent service returned error: %s", string(body))
	}

	var processes []*models.RunningProcess
	if err := json.NewDecoder(resp.Body).Decode(&processes); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	// Sort processes by name (case-insensitive)
	sort.Slice(processes, func(i, j int) bool {
		return strings.ToLower(processes[i].Name) < strings.ToLower(processes[j].Name)
	})

	return processes, nil
}

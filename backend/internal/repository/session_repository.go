package repository

import (
	"fmt"
	"os-pulse-backend/internal/models"
	"time"

	"gorm.io/gorm"
)

type SessionRepository struct {
	db *gorm.DB
}

func NewSessionRepository(db *gorm.DB) *SessionRepository {
	return &SessionRepository{db: db}
}

func (r *SessionRepository) CreateSession(session *models.Session) error {
	result := r.db.Create(session)
	if result.Error != nil {
		return fmt.Errorf("failed to create session: %w", result.Error)
	}
	return nil
}

func (r *SessionRepository) GetSessionByID(sessionID string) (*models.Session, error) {
	var session models.Session
	result := r.db.Where("id = ?", sessionID).First(&session)

	if result.Error != nil {
		if result.Error == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("session not found")
		}
		return nil, fmt.Errorf("failed to get session: %w", result.Error)
	}

	return &session, nil
}

func (r *SessionRepository) UpdateSessionMonitoringStarted(sessionID string, startTime time.Time) error {
	result := r.db.Model(&models.Session{}).
		Where("id = ?", sessionID).
		Updates(map[string]interface{}{
			"monitoring_started": startTime,
			"is_active":          true,
		})

	if result.Error != nil {
		return fmt.Errorf("failed to update session monitoring started: %w", result.Error)
	}

	if result.RowsAffected == 0 {
		return fmt.Errorf("session not found")
	}

	return nil
}

func (r *SessionRepository) UpdateSessionMonitoringEnded(sessionID string, endTime time.Time) error {
	result := r.db.Model(&models.Session{}).
		Where("id = ?", sessionID).
		Updates(map[string]interface{}{
			"monitoring_ended": endTime,
			"is_active":        false,
		})

	if result.Error != nil {
		return fmt.Errorf("failed to update session monitoring ended: %w", result.Error)
	}

	if result.RowsAffected == 0 {
		return fmt.Errorf("session not found")
	}

	return nil
}

func (r *SessionRepository) GetActiveSessions() ([]*models.Session, error) {
	var sessions []*models.Session
	result := r.db.Where("is_active = ?", true).Find(&sessions)

	if result.Error != nil {
		return nil, fmt.Errorf("failed to query active sessions: %w", result.Error)
	}

	return sessions, nil
}

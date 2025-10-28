package main

import (
	"fmt"
	"log"
	"time"

	"os-pulse-backend/internal/config"
	"os-pulse-backend/internal/database"
	"os-pulse-backend/internal/models"

	"github.com/google/uuid"
	"gorm.io/datatypes"
)

func main() {
	// Load configuration
	cfg := config.Load()

	// Initialize database
	db, err := database.Connect(cfg.DatabaseURL)
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}

	// Get underlying SQL DB for connection management
	sqlDB, err := db.DB()
	if err != nil {
		log.Fatal("Failed to get underlying SQL DB:", err)
	}
	defer sqlDB.Close()

	// Run migrations
	if err := database.Migrate(db); err != nil {
		log.Fatal("Failed to run migrations:", err)
	}

	fmt.Println("✅ Database connection and migration successful!")

	// Test creating a session
	session := &models.Session{
		ID:       uuid.New().String(),
		FileName: "test-file.txt",
		IsActive: false,
	}

	if err := db.Create(session).Error; err != nil {
		log.Fatal("Failed to create test session:", err)
	}

	fmt.Printf("✅ Created test session: %s\n", session.ID)

	// Test creating an event
	eventData := datatypes.JSON{}
	testData := map[string]interface{}{
		"filePath":  "C:\\test\\file.txt",
		"operation": "ReadFile",
		"metadata": map[string]interface{}{
			"processName": "notepad.exe",
			"processId":   1234,
			"sessionId":   session.ID,
		},
	}

	if err := eventData.Scan(testData); err != nil {
		log.Fatal("Failed to create test event data:", err)
	}

	event := &models.Event{
		SessionID: session.ID,
		EventType: "file_operation",
		Timestamp: time.Now(),
		Source:    "test",
		Data:      eventData,
		IsSent:    false,
	}

	if err := db.Create(event).Error; err != nil {
		log.Fatal("Failed to create test event:", err)
	}

	fmt.Printf("✅ Created test event: %d\n", event.ID)

	// Test querying events
	var events []models.Event
	if err := db.Where("session_id = ?", session.ID).Find(&events).Error; err != nil {
		log.Fatal("Failed to query events:", err)
	}

	fmt.Printf("✅ Found %d events for session\n", len(events))

	// Test updating session
	if err := db.Model(session).Update("is_active", true).Error; err != nil {
		log.Fatal("Failed to update session:", err)
	}

	fmt.Println("✅ Updated session status")

	// Clean up test data
	if err := db.Delete(&events).Error; err != nil {
		log.Printf("Warning: Failed to clean up test events: %v\n", err)
	}

	if err := db.Delete(session).Error; err != nil {
		log.Printf("Warning: Failed to clean up test session: %v\n", err)
	}

	fmt.Println("✅ Cleaned up test data")
	fmt.Println("🎉 GORM backend test completed successfully!")
}

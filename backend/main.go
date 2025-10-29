package main

import (
	"log"
	"os"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"

	"os-pulse-backend/internal/config"
	"os-pulse-backend/internal/database"
	"os-pulse-backend/internal/handlers"
	"os-pulse-backend/internal/repository"
	"os-pulse-backend/internal/service"
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

	// Initialize repositories
	eventRepo := repository.NewEventRepository(db)
	sessionRepo := repository.NewSessionRepository(db)

	// Initialize services
	eventService := service.NewEventService(eventRepo, sessionRepo, cfg.AgentServiceURL)
	sessionService := service.NewSessionService(sessionRepo, cfg.AgentServiceURL)

	// Initialize handlers
	eventHandler := handlers.NewEventHandler(eventService)
	frontendHandler := handlers.NewFrontendHandler(eventService, sessionService)

	// Initialize Echo
	e := echo.New()

	// Middleware
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())
	e.Use(middleware.CORS())

	// Agent routes (for receiving events from agent)
	e.POST("/api/events", eventHandler.ReceiveEvent)
	e.POST("/api/http/events", eventHandler.ReceiveHTTPEvent)
	e.POST("/api/net/events", eventHandler.ReceiveNetEvent)

	// Frontend routes (for serving frontend requests)
	e.POST("/api/create-session", frontendHandler.CreateSession)
	e.GET("/api/monitor-modes", frontendHandler.GetMonitorModes)
	e.POST("/api/start-monitor", frontendHandler.StartMonitor)
	e.POST("/api/monitor/stop", frontendHandler.StopMonitor)

	// Event retrieval endpoints (batch-based, no session required)
	e.GET("/api/events/:sessionId", frontendHandler.GetEvents) // Get unsent events in batches
	e.GET("/api/events/export", eventHandler.ExportEvents)     // Export all events as JSON
	e.POST("/api/list-processes", frontendHandler.ListProcesses)

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "3003"
	}

	log.Printf("Server starting on port %s", port)
	log.Fatal(e.Start(":" + port))
}

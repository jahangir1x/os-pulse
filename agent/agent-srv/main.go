package main

import (
	"log"
	"os"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

func main() {
	// Initialize Echo
	e := echo.New()

	// Middleware
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())
	e.Use(middleware.CORS())

	// Initialize handlers
	handler := NewHandler()

	// Routes
	e.POST("/api/upload-file", handler.UploadFile)
	e.POST("/api/list-processes", handler.ListProcesses)
	e.POST("/api/start-monitor", handler.StartMonitor)
	e.POST("/api/stop-monitor", handler.StopMonitor)

	// Health check
	e.GET("/health", func(c echo.Context) error {
		return c.JSON(200, map[string]string{"status": "ok"})
	})

	// Start server
	port := os.Getenv("AGENT_PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Agent service starting on port %s", port)
	log.Fatal(e.Start(":" + port))
}

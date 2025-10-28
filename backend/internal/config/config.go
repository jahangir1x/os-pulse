package config

import (
	"os"
)

type Config struct {
	DatabaseURL     string
	AgentServiceURL string
	Port            string
}

func Load() *Config {
	return &Config{
		DatabaseURL:     getEnv("DATABASE_URL", "postgres://postgres:password@localhost:5432/ospulse?sslmode=disable"),
		AgentServiceURL: getEnv("AGENT_SERVICE_URL", "http://localhost:7000"),
		Port:            getEnv("PORT", "3003"),
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

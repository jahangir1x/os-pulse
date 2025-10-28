# OS-Pulse Backend (GORM Version)

A Go backend service using Echo framework, GORM ORM, and PostgreSQL for the OS-Pulse monitoring system.

## Features

- RESTful API for frontend and agent communication
- GORM ORM with automatic migrations
- PostgreSQL database with JSONB support for event storage
- Session management with monitoring time tracking
- Event processing and forwarding
- File upload handling
- Automatic event marking and pagination

## Prerequisites

- Go 1.21 or higher
- PostgreSQL 12 or higher
- Agent service running on port 7000 (optional for full functionality)

## Setup

1. **Install dependencies:**
   ```bash
   go mod tidy
   ```

2. **Set up PostgreSQL:**
   ```bash
   # Create database
   createdb ospulse
   
   # Or using psql
   psql -c "CREATE DATABASE ospulse;"
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Run the application:**
   ```bash
   go run main.go
   ```

The server will start on port 3003 by default and automatically run GORM migrations.

## GORM Models

### Session Model
```go
type Session struct {
    ID                string     `gorm:"primaryKey;type:varchar(255)"`
    FileName          string     `gorm:"column:file_name;type:varchar(255);not null"`
    CreatedAt         time.Time  `gorm:"autoCreateTime"`
    UpdatedAt         time.Time  `gorm:"autoUpdateTime"`
    MonitoringStarted *time.Time `gorm:"column:monitoring_started"`
    MonitoringEnded   *time.Time `gorm:"column:monitoring_ended"`
    IsActive          bool       `gorm:"column:is_active;default:false"`
    Events            []Event    `gorm:"foreignKey:SessionID"`
}
```

### Event Model
```go
type Event struct {
    ID        uint64         `gorm:"primaryKey;autoIncrement"`
    SessionID string         `gorm:"column:session_id;type:varchar(255);not null;index"`
    EventType string         `gorm:"column:event_type;type:varchar(100);not null"`
    Timestamp time.Time      `gorm:"not null;index"`
    Source    string         `gorm:"type:varchar(100);not null"`
    Data      datatypes.JSON `gorm:"type:jsonb;not null"`
    IsSent    bool           `gorm:"column:is_sent;default:false;index"`
    CreatedAt time.Time      `gorm:"autoCreateTime"`
    UpdatedAt time.Time      `gorm:"autoUpdateTime"`
    Session   Session        `gorm:"foreignKey:SessionID;references:ID"`
}
```

## API Endpoints

### Frontend Endpoints

- `POST /api/create-session` - Create new monitoring session with file upload
- `GET /api/monitor-modes` - Get available monitoring modes
- `POST /api/start-monitor` - Start monitoring (forwards to agent service)
- `POST /api/monitor/stop` - Stop monitoring (forwards to agent service)
- `GET /api/events/:sessionId` - Get events for session (10 at a time)
- `POST /api/list-processes` - List running processes

### Agent Endpoints

- `POST /api/events/events` - Receive events from OS monitoring agent
- `POST /api/http/events` - Receive HTTP monitoring events
- `POST /api/net/events` - Receive network monitoring events

## GORM Features Used

### Automatic Migrations
- Tables are created automatically using `db.AutoMigrate()`
- Indexes are created based on struct tags
- Foreign key relationships are handled automatically

### JSONB Support
- Event data stored as PostgreSQL JSONB using `gorm.io/datatypes`
- Automatic serialization/deserialization of complex data structures

### Relationships
- One-to-many relationship between Sessions and Events
- Automatic foreign key constraints

### Query Optimization
- Strategic indexes on frequently queried fields
- Efficient pagination with LIMIT clauses
- Time-range queries for event filtering

## Repository Pattern with GORM

### Example Repository Method
```go
func (r *EventRepository) GetEventsBySessionInTimeRange(sessionID string, startTime, endTime *time.Time, limit int) ([]*models.Event, error) {
    var events []*models.Event
    query := r.db.Where("session_id = ? AND is_sent = ?", sessionID, false)

    if startTime != nil && endTime != nil {
        query = query.Where("timestamp BETWEEN ? AND ?", startTime, endTime)
    } else if startTime != nil {
        query = query.Where("timestamp >= ?", startTime)
    }

    result := query.Order("timestamp DESC").Limit(limit).Find(&events)
    return events, result.Error
}
```

## Configuration

Environment variables:

- `DATABASE_URL` - PostgreSQL connection string (default: `postgres://postgres:password@localhost:5432/ospulse?sslmode=disable`)
- `AGENT_SERVICE_URL` - URL of the agent service (default: `http://localhost:7000`)
- `PORT` - Server port (default: `3003`)

## Development

### Project Structure

```
backend/
├── main.go                     # Application entry point with GORM setup
├── go.mod                      # Go module with GORM dependencies
├── setup.bat & run.bat         # Windows convenience scripts
├── docker-compose.yml          # PostgreSQL setup
├── internal/
│   ├── config/                 # Environment configuration
│   ├── database/               # GORM connection and auto-migration
│   ├── models/                 # GORM models with struct tags
│   ├── repository/             # GORM-based data access layer
│   ├── service/                # Business logic layer
│   └── handlers/               # HTTP handlers
└── migrations/                 # Manual SQL migrations (optional)
```

### GORM Best Practices Used

1. **Struct Tags**: Proper column naming and constraints
2. **Associations**: Foreign key relationships
3. **Indexes**: Performance optimization
4. **Auto-timestamps**: CreatedAt/UpdatedAt fields
5. **JSON Handling**: Native JSONB support
6. **Error Handling**: Proper error checking and wrapping

### Adding New Models

1. Define struct with GORM tags in `internal/models/`
2. Add to `AutoMigrate()` call in `database/database.go`
3. Create repository methods using GORM query builder
4. GORM will handle table creation and relationships

## Database Migration

GORM automatically handles:
- Table creation
- Column additions/modifications
- Index creation
- Foreign key constraints

Manual migrations can still be used for complex schema changes.

## Performance Considerations

- **Preloading**: Use `Preload()` for related data when needed
- **Batch Operations**: GORM supports batch inserts/updates
- **Indexes**: Automatically created based on struct tags
- **Connection Pooling**: Handled by GORM's underlying driver

## Troubleshooting

### GORM Migration Issues
```bash
# Check if tables were created
psql $DATABASE_URL -c "\dt"
```

### GORM Query Debugging
Enable SQL logging in database connection:
```go
db, err := gorm.Open(postgres.Open(databaseURL), &gorm.Config{
    Logger: logger.Default.LogMode(logger.Info),
})
```

### JSON Data Issues
Ensure data structures implement proper JSON marshaling:
```go
type EventData struct {
    Field string `json:"field"`
}
```
package models

import (
	"time"

	"gorm.io/datatypes"
)

// Session represents a monitoring session
type Session struct {
	ID                string     `json:"sessionId" gorm:"primaryKey;type:varchar(255)"`
	FileName          string     `json:"fileName" gorm:"column:file_name;type:varchar(255);not null"`
	CreatedAt         time.Time  `json:"createdAt" gorm:"autoCreateTime"`
	UpdatedAt         time.Time  `json:"updatedAt" gorm:"autoUpdateTime"`
	MonitoringStarted *time.Time `json:"monitoringStarted,omitempty" gorm:"column:monitoring_started"`
	MonitoringEnded   *time.Time `json:"monitoringEnded,omitempty" gorm:"column:monitoring_ended"`
	IsActive          bool       `json:"isActive" gorm:"column:is_active;default:false"`
	Events            []Event    `json:"events,omitempty" gorm:"foreignKey:SessionID"`
}

// Event represents a system event from the agent
type Event struct {
	ID        uint64         `json:"id" gorm:"primaryKey;autoIncrement"`
	SessionID string         `json:"sessionId" gorm:"column:session_id;type:varchar(255);not null;index"`
	EventType string         `json:"event_type" gorm:"column:event_type;type:varchar(100);not null"`
	Timestamp time.Time      `json:"timestamp" gorm:"not null;index"`
	Source    string         `json:"source" gorm:"type:varchar(100);not null"`
	Data      datatypes.JSON `json:"data" gorm:"type:jsonb;not null"`
	IsSent    bool           `json:"isSent" gorm:"column:is_sent;default:false;index"`
	CreatedAt time.Time      `json:"createdAt" gorm:"autoCreateTime"`
	UpdatedAt time.Time      `json:"updatedAt" gorm:"autoUpdateTime"`
	Session   Session        `json:"session,omitempty" gorm:"foreignKey:SessionID;references:ID"`
}

// EventData represents the nested data structure in events
type EventData struct {
	Handle           *string    `json:"handle,omitempty"`
	FilePath         *string    `json:"filePath,omitempty"`
	BytesTransferred *int       `json:"bytesTransferred,omitempty"`
	Content          *string    `json:"content,omitempty"`
	Timestamp        *time.Time `json:"timestamp,omitempty"`
	Operation        *string    `json:"operation,omitempty"`
	ProcessHandle    *string    `json:"processHandle,omitempty"`
	ThreadHandle     *string    `json:"threadHandle,omitempty"`
	ImagePath        *string    `json:"imagePath,omitempty"`
	CommandLine      *string    `json:"commandLine,omitempty"`
	CurrentDirectory *string    `json:"currentDirectory,omitempty"`
	Status           *int       `json:"status,omitempty"`
	Metadata         *Metadata  `json:"metadata,omitempty"`
}

// Metadata represents the metadata in event data
type Metadata struct {
	SessionID   string `json:"sessionId"`
	ProcessName string `json:"processName"`
	ProcessID   int    `json:"processId"`
}

// HTTPEvent represents HTTP monitoring events
type HTTPEvent struct {
	TimestampMS int64       `json:"timestamp_ms"`
	Kind        string      `json:"kind"`
	Client      interface{} `json:"client"`
	Server      *Server     `json:"server"`
	Request     *Request    `json:"request"`
	Response    *Response   `json:"response"`
}

type Server struct {
	IP []interface{} `json:"ip"`
}

type Request struct {
	Method      string            `json:"method"`
	Scheme      string            `json:"scheme"`
	Host        string            `json:"host"`
	Port        int               `json:"port"`
	Path        string            `json:"path"`
	URL         string            `json:"url"`
	HTTPVersion string            `json:"http_version"`
	Headers     map[string]string `json:"headers"`
	Body        *Body             `json:"body"`
}

type Response struct {
	StatusCode  int               `json:"status_code"`
	Reason      string            `json:"reason"`
	HTTPVersion string            `json:"http_version"`
	Headers     map[string]string `json:"headers"`
	Body        *Body             `json:"body"`
}

type Body struct {
	Type       string `json:"type"`
	Content    string `json:"content,omitempty"`
	ContentB64 string `json:"content_b64,omitempty"`
	Size       int    `json:"size"`
	Truncated  bool   `json:"truncated"`
}

// NetworkEvent represents network monitoring events
type NetworkEvent struct {
	Events []NetworkEventItem `json:"events"`
}

type NetworkEventItem struct {
	Timestamp   float64 `json:"timestamp"`
	FrameNumber int     `json:"frame_number"`
	Protocol    string  `json:"protocol"`
	Src         string  `json:"src"`
	Dst         string  `json:"dst"`
	SrcPort     *int    `json:"src_port"`
	DstPort     *int    `json:"dst_port"`
	Length      int     `json:"length"`
	Info        string  `json:"info"`
	InfoRaw     string  `json:"info_raw"`
}

// MonitorMode represents available monitoring modes
type MonitorMode struct {
	ID   int    `json:"id"`
	Mode string `json:"mode"`
}

// RunningProcess represents a running process
type RunningProcess struct {
	PID  int    `json:"pid"`
	Name string `json:"name"`
}

// StartMonitorRequest represents the request to start monitoring
type StartMonitorRequest struct {
	SessionID string `json:"sessionId"`
	Mode      int    `json:"mode"`
	Processes []int  `json:"processes,omitempty"`
}

// StopMonitorRequest represents the request to stop monitoring
type StopMonitorRequest struct {
	SessionID string `json:"sessionId"`
}

// CreateSessionResponse represents the response for session creation
type CreateSessionResponse struct {
	SessionID string `json:"sessionId"`
}

// MessageResponse represents a generic message response
type MessageResponse struct {
	Message string `json:"message"`
}

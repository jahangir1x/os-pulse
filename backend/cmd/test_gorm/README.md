# GORM Database Test Utility

This utility tests the GORM database connection, migrations, and basic CRUD operations.

## Prerequisites

1. PostgreSQL database running (via Docker or local installation)
2. Database configured in `.env` file or environment variables

## Steps to Run

### 1. Ensure PostgreSQL is Running

If using Docker:
```bash
cd C:\Users\rocky\Desktop\dev\sandbox\os-pulse\backend
docker-compose up -d
```

### 2. Set Environment Variables

Make sure your `.env` file in the backend root has:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ospulse?sslmode=disable
AGENT_SERVICE_URL=http://localhost:8080
```

### 3. Run the Test

From the backend directory:
```bash
cd C:\Users\rocky\Desktop\dev\sandbox\os-pulse\backend
go run cmd/test_gorm/main.go
```

Or build and run:
```bash
cd C:\Users\rocky\Desktop\dev\sandbox\os-pulse\backend
go build -o cmd/test_gorm/test_gorm.exe cmd/test_gorm/main.go
.\cmd\test_gorm\test_gorm.exe
```

## What This Test Does

1. ✅ Connects to PostgreSQL database
2. ✅ Runs GORM migrations (creates Sessions and Events tables)
3. ✅ Creates a test session
4. ✅ Creates a test event with JSONB data
5. ✅ Queries events by session ID
6. ✅ Updates session status
7. ✅ Cleans up test data

## Expected Output

```
✅ Database connection and migration successful!
✅ Created test session: <uuid>
✅ Created test event: <id>
✅ Found 1 events for session
✅ Updated session status
✅ Cleaned up test data
🎉 GORM backend test completed successfully!
```

## Troubleshooting

### "Failed to connect to database"
- Check if PostgreSQL is running: `docker ps` or check local PostgreSQL service
- Verify DATABASE_URL in `.env` file
- Ensure port 5432 is not blocked

### "Failed to run migrations"
- Database user needs CREATE TABLE permissions
- Check database exists: `ospulse`

### Module errors
Run from backend directory:
```bash
cd C:\Users\rocky\Desktop\dev\sandbox\os-pulse\backend
go mod tidy
go run cmd/test_gorm/main.go
```

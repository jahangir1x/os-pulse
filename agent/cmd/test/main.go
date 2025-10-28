package main

import (
	"fmt"
	"os/exec"
	"runtime"
	"time"
)

func main() {
	var c *exec.Cmd

	switch runtime.GOOS {
	case "windows":
		// Use main.py instead of test.py - test.py has input() which causes EOF error
		c = exec.Command("python", "C:\\Users\\rocky\\Desktop\\dev\\sandbox\\os-pulse\\agent\\controller\\main.py", "spawn", "--executable", "C:\\Windows\\System32\\Notepad.exe")

	default: //Mac & Linux
		c = exec.Command("rm", "-f", "/d/a.txt")
	}

	// Start the command (non-blocking)
	fmt.Println("Starting Python controller to spawn Notepad...")
	err := c.Start()
	if err != nil {
		fmt.Printf("Failed to start command: %v\n", err)
		return
	}

	fmt.Printf("Python controller started with PID: %d\n", c.Process.Pid)
	fmt.Println("The controller will spawn and monitor Notepad.exe")
	fmt.Println("Check Task Manager for:")
	fmt.Println("  - python.exe (the controller)")
	fmt.Println("  - Notepad.exe (the spawned process)")
	fmt.Println("\nMain process will sleep for 2000 seconds...")

	// Wait for the process in a goroutine
	go func() {
		waitErr := c.Wait()
		if waitErr != nil {
			fmt.Printf("\nPython controller exited with error: %v\n", waitErr)
		} else {
			fmt.Println("\nPython controller exited successfully")
		}
	}()

	// Sleep for 2000 seconds
	time.Sleep(2000 * time.Second)

	fmt.Println("Sleep completed. Exiting...")
}

package main

import (
	"fmt"
	"os"

	"github.com/fatih/color"
	"github.com/spf13/cobra"
)

func main() {
	var rootCmd = &cobra.Command{
		Use:   "os-pulse",
		Short: "OS-Pulse Windows System Monitor Controller",
		Long: `A Windows system monitoring framework with Frida-based instrumentation.
		
Monitor file operations and process creation activities in real-time with
optional forwarding to external APIs for SIEM and analytics integration.`,
		Run: func(cmd *cobra.Command, args []string) {
			printBanner()
			cmd.Help()
		},
	}

	// Add commands
	rootCmd.AddCommand(createListCommand())
	rootCmd.AddCommand(createSpawnCommand())
	rootCmd.AddCommand(createAttachCommand())

	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

func printBanner() {
	cyan := color.New(color.FgCyan)
	cyan.Println("╔═══════════════════════════════════════════════════════════╗")
	cyan.Println("║                     OS-Pulse Controller                   ║")
	cyan.Println("║              Windows System Monitor v1.0                 ║")
	cyan.Println("╚═══════════════════════════════════════════════════════════╝")
}

func createListCommand() *cobra.Command {
	var filter string

	cmd := &cobra.Command{
		Use:   "list",
		Short: "List running processes",
		Long:  "List all running processes with optional name filtering",
		Run: func(cmd *cobra.Command, args []string) {
			controller := NewFridaController()
			controller.ListProcesses(filter)
		},
	}

	cmd.Flags().StringVarP(&filter, "filter", "f", "", "Filter processes by name")
	return cmd
}

func createSpawnCommand() *cobra.Command {
	var executable string
	var apiEndpoint string
	var apiKey string
	var enableAPI bool

	cmd := &cobra.Command{
		Use:   "spawn",
		Short: "Spawn a new process with monitoring",
		Long:  "Start a new process under Frida monitoring with real-time event capture",
		Run: func(cmd *cobra.Command, args []string) {
			controller := NewFridaController()
			if enableAPI {
				controller.EnableAPI(apiEndpoint, apiKey)
			}
			controller.SpawnProcess(executable)
		},
	}

	cmd.Flags().StringVarP(&executable, "executable", "e", "", "Path to executable to spawn (required)")
	cmd.Flags().StringVar(&apiEndpoint, "api-endpoint", "", "API endpoint URL for event forwarding")
	cmd.Flags().StringVar(&apiKey, "api-key", "", "API key for authentication")
	cmd.Flags().BoolVar(&enableAPI, "enable-api", false, "Enable API event forwarding")
	cmd.MarkFlagRequired("executable")

	return cmd
}

func createAttachCommand() *cobra.Command {
	var processName string
	var processID int
	var apiEndpoint string
	var apiKey string
	var enableAPI bool

	cmd := &cobra.Command{
		Use:   "attach",
		Short: "Attach to an existing process",
		Long:  "Attach to a running process by name or PID for monitoring",
		Run: func(cmd *cobra.Command, args []string) {
			controller := NewFridaController()
			if enableAPI {
				controller.EnableAPI(apiEndpoint, apiKey)
			}

			if processName != "" {
				controller.AttachToProcessByName(processName)
			} else if processID > 0 {
				controller.AttachToProcessByPID(processID)
			}
		},
	}

	cmd.Flags().StringVarP(&processName, "process-name", "n", "", "Name of process to attach to")
	cmd.Flags().IntVarP(&processID, "process-id", "p", 0, "PID of process to attach to")
	cmd.Flags().StringVar(&apiEndpoint, "api-endpoint", "", "API endpoint URL for event forwarding")
	cmd.Flags().StringVar(&apiKey, "api-key", "", "API key for authentication")
	cmd.Flags().BoolVar(&enableAPI, "enable-api", false, "Enable API event forwarding")

	return cmd
}

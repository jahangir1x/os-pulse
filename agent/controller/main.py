"""
Main entry point for the OS-Pulse Controller
"""
import sys
import argparse
from pathlib import Path
from colorama import Fore, Style, init

from frida_controller import FridaController

# Initialize colorama
init(autoreset=True)


def print_banner():
    """Print application banner"""
    print(f"{Fore.CYAN}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                     OS-Pulse Controller                   ║")
    print("║              Windows System Monitor v1.0                 ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")


def list_processes_command(args):
    """List running processes"""
    controller = FridaController()
    processes = controller.list_processes(args.filter)
    
    if not processes:
        print(f"{Fore.YELLOW}No processes found")
        return
    
    print(f"\n{Fore.GREEN}Running Processes:")
    print(f"{Fore.WHITE}{'PID':<8} {'Name':<20} {'Executable':<50}")
    print(f"{Fore.WHITE}{'-' * 80}")
    
    for proc in processes[:20]:  # Limit to first 20 results
        pid = proc['pid']
        name = proc['name'][:19] if proc['name'] else 'Unknown'
        exe = proc['exe'][:49] if proc['exe'] else 'Unknown'
        print(f"{Fore.CYAN}{pid:<8} {name:<20} {exe:<50}")
    
    if len(processes) > 20:
        print(f"{Fore.YELLOW}... and {len(processes) - 20} more processes")


def spawn_command(args):
    """Spawn a new process with monitoring"""
    controller = FridaController()
    
    if controller.spawn_process(args.executable, args.args):
        print(f"{Fore.GREEN}Successfully spawned and attached to process")
        controller.start_monitoring()
    else:
        print(f"{Fore.RED}Failed to spawn process")
        sys.exit(1)


def attach_command(args):
    """Attach to existing process(es)"""
    controller = FridaController()
    
    if args.all:
        # Attach to all processes
        success = controller.attach_to_all_processes(filter_name=args.filter)
    elif args.pids:
        # Attach to multiple PIDs
        success = controller.attach_to_multiple_pids(args.pids)
    elif args.pid:
        # Attach to single PID
        success = controller.attach_to_process(pid=args.pid)
    elif args.process_name:
        # Attach to single process name
        success = controller.attach_to_process(process_name=args.process_name)
    else:
        print(f"{Fore.RED}Must specify --pid, --pids, --process-name, or --all")
        sys.exit(1)
    
    if success:
        print(f"{Fore.GREEN}Successfully attached to process(es)")
        controller.start_monitoring()
    else:
        print(f"{Fore.RED}Failed to attach to process(es)")
        sys.exit(1)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="OS-Pulse Controller - Windows System Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py spawn --executable "C:\\Windows\\System32\\notepad.exe"
  python main.py attach --process-name "notepad.exe"
  python main.py attach --pid 1234
  python main.py attach --pids 1234 5678 9012
  python main.py attach --all
  python main.py attach --all --filter notepad
  python main.py list-processes
  python main.py list-processes --filter notepad
        """
    )
    
    parser.add_argument(
        '--agent-script', 
        type=str, 
        help='Path to the Frida agent script (default: ../injector/_agent.js)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Spawn command
    spawn_parser = subparsers.add_parser('spawn', help='Spawn a new process with monitoring')
    spawn_parser.add_argument('--executable', required=True, help='Path to executable to spawn')
    spawn_parser.add_argument('--args', nargs='*', help='Arguments to pass to the executable')
    spawn_parser.set_defaults(func=spawn_command)
    
    # Attach command
    attach_parser = subparsers.add_parser('attach', help='Attach to existing process(es)')
    attach_group = attach_parser.add_mutually_exclusive_group(required=True)
    attach_group.add_argument('--process-name', help='Name of process to attach to')
    attach_group.add_argument('--pid', type=int, help='PID of process to attach to')
    attach_group.add_argument('--pids', type=int, nargs='+', help='Multiple PIDs to attach to')
    attach_group.add_argument('--all', action='store_true', help='Attach to all processes')
    attach_parser.add_argument('--filter', help='Filter processes by name (used with --all)')
    attach_parser.set_defaults(func=attach_command)
    
    # List processes command
    list_parser = subparsers.add_parser('list-processes', help='List running processes')
    list_parser.add_argument('--filter', help='Filter processes by name')
    list_parser.set_defaults(func=list_processes_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Check if command was provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Execute command
        args.func(args)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

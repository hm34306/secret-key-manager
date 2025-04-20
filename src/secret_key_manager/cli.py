"""Command-line interface for the Secret Key Manager."""

import sys
import argparse
import logging

# Import all providers to ensure they're registered
from secret_key_manager import keys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_argparse() -> argparse.ArgumentParser:
    """Set up command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Secret Key Manager command-line interface",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Global arguments
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # 'get' command
    get_parser = subparsers.add_parser(
        "get", help="Get a key", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    get_parser.add_argument("key_name", help="Name of the key to get")
    get_parser.add_argument(
        "--provider",
        "-p",
        action="append",
        help="Specific provider(s) to use (can be specified multiple times)",
    )

    # 'set' command
    set_parser = subparsers.add_parser(
        "set",
        help="Set a key value and optionally persist it to providers",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    set_parser.add_argument("key_name", help="Name of the key to set")
    set_parser.add_argument("key_value", help="Value to set the key to")
    set_parser.add_argument(
        "--provider",
        "-p",
        action="append",
        help="Specific provider(s) to use for persistence (can be specified multiple times)",
    )
    set_parser.add_argument(
        "--no-persist",
        action="store_true",
        help="Do not persist the key to any provider (only store in memory)",
    )

    # 'providers' command
    providers_parser = subparsers.add_parser(
        "providers",
        help="Manage key providers",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    providers_subparsers = providers_parser.add_subparsers(
        dest="providers_command", help="Providers command"
    )

    # 'providers list' command
    providers_subparsers.add_parser(
        "list",
        help="List registered providers",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # 'providers enable' command
    providers_enable_parser = providers_subparsers.add_parser(
        "enable",
        help="Enable a provider",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    providers_enable_parser.add_argument("name", help="Name of the provider to enable")

    # 'providers disable' command
    providers_disable_parser = providers_subparsers.add_parser(
        "disable",
        help="Disable a provider",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    providers_disable_parser.add_argument(
        "name", help="Name of the provider to disable"
    )

    # 'providers status' command
    providers_subparsers.add_parser(
        "status",
        help="Show provider status",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # 'providers writable' command
    providers_subparsers.add_parser(
        "writable",
        help="List providers that support writing keys",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    return parser


def handle_get_command(args: argparse.Namespace) -> int:
    """Handle the 'get' command."""
    key_value = keys.get_key(args.key_name, args.provider)
    if key_value:
        print(key_value)
        return 0
    else:
        providers_tried = args.provider if args.provider else keys.get_providers()
        logger.error(
            f"Key '{args.key_name}' not found in any of the providers: {', '.join(providers_tried)}"
        )
        return 1


def handle_set_command(args: argparse.Namespace) -> int:
    """Handle the 'set' command."""
    # Determine if we should persist the key
    persist = not args.no_persist

    # If persisting, check if any providers support writing
    if persist:
        writable_providers = keys.get_writable_providers()

        # Filter to specified providers if provided
        if args.provider:
            writable_providers = [p for p in writable_providers if p in args.provider]

        if not writable_providers:
            logger.warning("No writable providers available")
            if args.provider:
                logger.error(
                    f"Specified providers {args.provider} do not support writing"
                )
                return 1
            else:
                logger.warning("Key will only be stored in memory")
                persist = False

    # Set the key
    result = keys.set_key(
        args.key_name, args.key_value, persist=persist, providers=args.provider
    )

    # Report success or failure
    if result or not persist:
        print(f"Key '{args.key_name}' set successfully")
        if persist:
            print(
                f"Key persisted to providers: {', '.join(args.provider) if args.provider else 'all writable providers'}"
            )
        else:
            print("Key stored in memory only (not persisted)")
        return 0
    else:
        logger.error(f"Failed to persist key '{args.key_name}'")
        return 1


def handle_providers_list_command(args: argparse.Namespace) -> int:
    """Handle the 'providers list' command."""
    providers = keys.get_providers()

    if not providers:
        print("No active providers")
        return 0

    print("Active providers:")
    for provider in providers:
        print(f"  - {provider}")

    return 0


def handle_providers_enable_command(args: argparse.Namespace) -> int:
    """Handle the 'providers enable' command."""
    if keys.enable_provider(args.name):
        print(f"Provider '{args.name}' enabled")
        return 0
    else:
        logger.error(f"Provider '{args.name}' not found")
        return 1


def handle_providers_disable_command(args: argparse.Namespace) -> int:
    """Handle the 'providers disable' command."""
    if keys.disable_provider(args.name):
        print(f"Provider '{args.name}' disabled")
        return 0
    else:
        logger.error(f"Provider '{args.name}' not found")
        return 1


def handle_providers_status_command(args: argparse.Namespace) -> int:
    """Handle the 'providers status' command."""
    provider_status = keys.get_provider_status()

    if not provider_status:
        print("No providers registered")
        return 0

    print("Provider status:")

    # Find the maximum length for nice formatting
    max_name_length = (
        max([len(name) for name in provider_status.keys()]) if provider_status else 0
    )

    # Print status table header
    print(
        f"  {'PROVIDER':{max_name_length}}  {'PRIORITY':<10}  {'STATUS':<10}  {'WRITABLE':<10}  {'CLASS'}"
    )
    print(f"  {'-' * max_name_length}  {'-' * 10}  {'-' * 10}  {'-' * 10}  {'-' * 20}")

    # Sort by priority
    sorted_providers = sorted(provider_status.items(), key=lambda x: x[1]["priority"])

    for name, info in sorted_providers:
        status = "Enabled" if info["enabled"] else "Disabled"
        writable = "Yes" if info.get("supports_write", False) else "No"
        print(
            f"  {name:{max_name_length}}  {info['priority']:<10}  {status:<10}  {writable:<10}  {info['class']}"
        )

    return 0


def handle_providers_writable_command(args: argparse.Namespace) -> int:
    """Handle the 'providers writable' command."""
    writable_providers = keys.get_writable_providers()

    if not writable_providers:
        print("No writable providers available")
        return 0

    print("Writable providers:")
    for provider in writable_providers:
        print(f"  - {provider}")

    return 0


def handle_providers_command(args: argparse.Namespace) -> int:
    """Handle the 'providers' command and its subcommands."""
    if not args.providers_command:
        logger.error("No providers subcommand specified")
        return 1

    if args.providers_command == "list":
        return handle_providers_list_command(args)
    elif args.providers_command == "enable":
        return handle_providers_enable_command(args)
    elif args.providers_command == "disable":
        return handle_providers_disable_command(args)
    elif args.providers_command == "status":
        return handle_providers_status_command(args)
    elif args.providers_command == "writable":
        return handle_providers_writable_command(args)
    else:
        logger.error(f"Unknown providers subcommand: {args.providers_command}")
        return 1


def main() -> int:
    """Main entry point for the CLI."""
    parser = setup_argparse()
    args = parser.parse_args()

    # Set up logging based on verbosity flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # If no command is specified, show help
    if not args.command:
        parser.print_help()
        return 1

    # Handle commands
    if args.command == "get":
        return handle_get_command(args)
    elif args.command == "set":
        return handle_set_command(args)
    elif args.command == "providers":
        return handle_providers_command(args)
    else:
        logger.error(f"Unknown command: {args.command}")
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

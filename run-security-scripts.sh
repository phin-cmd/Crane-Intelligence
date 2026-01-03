#!/bin/bash

# Helper script to run security scripts from any directory
# Usage: ./run-security-scripts.sh [script_name] [arguments]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

SCRIPT_NAME="${1:-help}"

case "$SCRIPT_NAME" in
    test|test_security|test-security)
        shift
        exec "$SCRIPT_DIR/test_security.sh" "$@"
        ;;
    monitor|monitor_security|monitor-security)
        shift
        exec "$SCRIPT_DIR/monitor_security.sh" "$@"
        ;;
    restart|restart-backend|restart_backend)
        shift
        exec "$SCRIPT_DIR/restart-backend-secure.sh" "$@"
        ;;
    verify|verify-scripts)
        exec "$SCRIPT_DIR/verify-scripts.sh"
        ;;
    help|--help|-h)
        echo "Security Scripts Runner"
        echo ""
        echo "Usage: $0 [script] [arguments]"
        echo ""
        echo "Available scripts:"
        echo "  test, test_security, test-security    - Run security tests"
        echo "  monitor, monitor_security             - Monitor security events"
        echo "  restart, restart-backend               - Restart backend securely"
        echo "  verify, verify-scripts                - Verify all scripts"
        echo ""
        echo "Examples:"
        echo "  $0 test http://localhost:8004"
        echo "  $0 monitor monitor"
        echo "  $0 restart"
        echo ""
        echo "Scripts location: $SCRIPT_DIR"
        exit 0
        ;;
    *)
        echo "Unknown script: $SCRIPT_NAME"
        echo "Run '$0 help' for usage"
        exit 1
        ;;
esac


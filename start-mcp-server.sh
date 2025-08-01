#!/bin/bash

# Start macOS UI Automation MCP Server
# This script manages the MCP server lifecycle with proper cleanup

set -e

SERVER_NAME="mcp-macos-ui"
PID_FILE="/tmp/mcp-macos-ui.pid"
LOG_FILE="/tmp/mcp-macos-ui.log"

# Function to cleanup existing server
cleanup_server() {
    echo "🧹 Cleaning up existing MCP server processes..."
    
    # Kill by PID file if it exists
    if [ -f "$PID_FILE" ]; then
        local PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "   🔪 Killing existing server (PID: $PID)"
            kill "$PID" 2>/dev/null || true
            sleep 1
            # Force kill if still running
            kill -9 "$PID" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
    fi
    
    # Kill any Python processes running our server
    pkill -f "mcp_server.py" 2>/dev/null || true
    pkill -f "mcp-macos-ui" 2>/dev/null || true
    sleep 1
    
    echo "   ✅ Cleanup complete"
}

# Function to start server
start_server() {
    echo "🚀 Starting macOS UI Automation MCP Server..."
    
    # Ensure we're in the correct directory
    cd "$(dirname "$0")"
    
    # Start server in background with nohup (headless mode for Claude)
    nohup poetry run python src/macos_ui_automation/mcp_server.py --transport stdio > "$LOG_FILE" 2>&1 &
    local PID=$!
    
    # Save PID for cleanup
    echo "$PID" > "$PID_FILE"
    
    # Wait a moment and check if it's still running
    sleep 2
    if kill -0 "$PID" 2>/dev/null; then
        echo "   ✅ Server started successfully (PID: $PID)"
        echo "   📄 Logs: tail -f $LOG_FILE"
        echo "   🛑 Stop: $0 stop"
        return 0
    else
        echo "   ❌ Server failed to start"
        echo "   📄 Check logs: cat $LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Function to stop server
stop_server() {
    echo "🛑 Stopping MCP server..."
    cleanup_server
    rm -f "$LOG_FILE"
    echo "   ✅ Server stopped"
}

# Function to show server status
show_status() {
    if [ -f "$PID_FILE" ]; then
        local PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "✅ MCP server is running (PID: $PID)"
            echo "   📄 Logs: tail -f $LOG_FILE"
            return 0
        else
            echo "❌ MCP server is not running (stale PID file)"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        echo "❌ MCP server is not running"
        return 1
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo "📄 MCP Server logs:"
        tail -f "$LOG_FILE"
    else
        echo "❌ No log file found at $LOG_FILE"
        exit 1
    fi
}

# Function to test server with MCP inspector
test_server() {
    echo "🧪 Testing MCP server with inspector..."
    
    # Check if server is running
    if ! show_status > /dev/null; then
        echo "❌ Server is not running. Start it first with: $0 start"
        exit 1
    fi
    
    # Start MCP inspector pointing to our server
    echo "🔍 Starting MCP Inspector..."
    echo "   🌐 This will open your browser to test the server"
    
    # Use MCP CLI to test our server (this will open browser)
    poetry run mcp dev src/macos_ui_automation/mcp_server.py
}

# Main script logic
case "${1:-start}" in
    "start")
        cleanup_server
        start_server
        ;;
    "stop")
        stop_server
        ;;
    "restart")
        stop_server
        sleep 1
        start_server
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "test")
        test_server
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|test}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the MCP server in background"
        echo "  stop    - Stop the MCP server"
        echo "  restart - Restart the MCP server"
        echo "  status  - Show server status"
        echo "  logs    - Show and follow server logs"
        echo "  test    - Test server with MCP inspector"
        echo ""
        echo "Examples:"
        echo "  $0 start     # Start server"
        echo "  $0 logs      # Watch logs"
        echo "  $0 test      # Test with inspector"
        exit 1
        ;;
esac
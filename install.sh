#!/usr/bin/env bash
# NullTrace — install.sh
# Maintained by: krypthane | github.com/wavegxz-design

set -e

echo ""
echo "  ┌──────────────────────────────────┐"
echo "  │  NullTrace v1.0 — Install       │"
echo "  │  krypthane | wavegxz-design     │"
echo "  └──────────────────────────────────┘"
echo ""

# Python 3.8+ check
if ! python3 -c "import sys; assert sys.version_info >= (3,8)" 2>/dev/null; then
    echo "  [!] Python 3.8+ is required."
    exit 1
fi

echo "  [+] Python version OK"

# Create launcher
INSTALL_DIR="/usr/local/bin"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -w "$INSTALL_DIR" ] || [ "$(id -u)" -eq 0 ]; then
    cat > "$INSTALL_DIR/nulltrace" << EOF
#!/usr/bin/env bash
cd "$SCRIPT_DIR"
python3 nulltrace.py "\$@"
EOF
    chmod +x "$INSTALL_DIR/nulltrace"
    echo "  [+] Launcher created: nulltrace"
else
    echo "  [!] No write access to $INSTALL_DIR — run with sudo or add manually."
fi

echo ""
echo "  [✔] Installation complete."
echo "  [>] Run: python3 nulltrace.py"
echo ""

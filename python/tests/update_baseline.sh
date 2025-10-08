#!/bin/bash
# Update baseline script - backs up old baseline and creates new one

cd "$(dirname "$0")"

echo "This will replace the current baseline with batch_tests output."
echo "The old baseline will be backed up with a timestamp."
echo ""
read -p "Are you sure? (yes/no): " -r
echo

if [[ $REPLY =~ ^[Yy]es$ ]]; then
    python regression_test.py --create-baseline
    echo ""
    echo "✓ Baseline updated successfully!"
else
    echo "Cancelled."
fi

#!/bin/zsh
# =============================================================================
# install_launchd.sh -- schedule daily_run.sh on macOS, weekdays at 15:00 SGT.
#
# WHY 15:00 SGT
#     The US close is 04:00 SGT the following morning, so an 15:00 run captures
#     the PREVIOUS US session, which is the last one whose bar is complete. The
#     forward log already refuses any bar from an incomplete session -- that
#     guard was added on 2026-08-20 after a live partial bar was accepted two
#     minutes into a session -- so a mistimed run is caught rather than logged.
#
# WHY launchd AND NOT cron
#     cron does not run if the Mac was asleep at the scheduled minute. launchd
#     with RunAtLoad plus StartCalendarInterval catches up on the next wake,
#     which for a laptop is the difference between a daily log and a log full
#     of holes.
#
# WHAT IT DOES NOT DO
#     It does not pass --no-read, so the nightly job WILL spend money, capped
#     at 40 new documents. To schedule a free version, edit the plist's
#     ProgramArguments to add --no-read before installing.
#
# Install:    ./install_launchd.sh
# Check:      launchctl list | grep regimeaware
# Run now:    launchctl kickstart -k gui/$(id -u)/com.regimeaware.daily
# Remove:     launchctl bootout gui/$(id -u)/com.regimeaware.daily
# =============================================================================
set -e
REPO="$(cd "$(dirname "$0")" && pwd)"
LABEL="com.regimeaware.daily"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

chmod +x "$REPO/daily_run.sh"
mkdir -p "$HOME/Library/LaunchAgents" "$REPO/logs"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>$REPO/daily_run.sh</string>
  </array>
  <key>WorkingDirectory</key><string>$REPO</string>
  <key>StandardOutPath</key><string>$REPO/logs/launchd.out</string>
  <key>StandardErrorPath</key><string>$REPO/logs/launchd.err</string>
  <key>RunAtLoad</key><false/>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
  </array>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "installed: $PLIST"
echo "weekdays 15:00. Verify with:  launchctl list | grep regimeaware"
echo "Test it now without waiting:  launchctl kickstart -k gui/$(id -u)/$LABEL"
echo "Then read:                    tail -40 $REPO/logs/daily_\$(date +%Y%m%d).log"

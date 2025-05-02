#!/bin/bash

# Output directory
REPORT_DIR="/tmp/system_reports"
mkdir -p "$REPORT_DIR"

# Workaround for Non-Root Users (FIO Directory)
FIO_DIR="$HOME/fio_test"
mkdir -p "$FIO_DIR"

# Timestamp
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Report File Paths
TEXT_REPORT="$REPORT_DIR/system_report_$TIMESTAMP.txt"
JSON_REPORT="$REPORT_DIR/fio_report_$TIMESTAMP.json"
CSV_REPORT="$REPORT_DIR/system_report_$TIMESTAMP.csv"
HTML_REPORT="$REPORT_DIR/system_report_$TIMESTAMP.html"

# Initialize CSV
echo "Category,Key,Value" > "$CSV_REPORT"

# Start HTML Report
echo "<html><head><title>System Report - $TIMESTAMP</title></head><body>" > "$HTML_REPORT"
echo "<h1>📄 System Report - $TIMESTAMP</h1>" >> "$HTML_REPORT"

# Collect Hardware Information
collect_hardware_info() {
    echo "🚀 Collecting Hardware Information..." | tee -a "$TEXT_REPORT"
    echo "<h2>🔹 Hardware Information</h2>" >> "$HTML_REPORT"

    # CPU Info
    echo "<h3>💻 CPU Information</h3><pre>" >> "$HTML_REPORT"
    lscpu | tee -a "$TEXT_REPORT" | tee -a "$HTML_REPORT"
    echo "</pre>" >> "$HTML_REPORT"

    # RAM Info
    echo "<h3>🖥️ RAM Information</h3><pre>" >> "$HTML_REPORT"
    free -h | tee -a "$TEXT_REPORT" | tee -a "$HTML_REPORT"
    echo "</pre>" >> "$HTML_REPORT"

    # Disk Info
    echo "<h3>💾 Disk Information</h3><pre>" >> "$HTML_REPORT"
    lsblk -o NAME,SIZE,TYPE,MOUNTPOINT | tee -a "$TEXT_REPORT" | tee -a "$HTML_REPORT"
    df -h | tee -a "$TEXT_REPORT" | tee -a "$HTML_REPORT"
    echo "</pre>" >> "$HTML_REPORT"
}

# Collect User & Security Information
collect_user_security_info() {
    echo "🔐 Collecting User & Security Information..." | tee -a "$TEXT_REPORT"
    echo "<h2>🔒 Security & User Information</h2>" >> "$HTML_REPORT"

    # Last Password Change Dates
    echo "<h3>📅 Last Password Change Dates</h3><pre>" >> "$HTML_REPORT"
    while IFS=: read -r user _; do
        LAST_CHANGE=$(chage -l "$user" 2>/dev/null | grep "Last password change" | cut -d: -f2)
        echo "$user: $LAST_CHANGE" | tee -a "$TEXT_REPORT" >> "$HTML_REPORT"
        echo "User,Last Password Change,$LAST_CHANGE" >> "$CSV_REPORT"
    done < <(getent passwd | awk -F: '$3 >= 1000 {print $1}')
    echo "</pre>" >> "$HTML_REPORT"

    # Account Status
    echo "<h3>🆔 Account Status</h3><pre>" >> "$HTML_REPORT"
    while IFS=: read -r user _; do
        STATUS=$(passwd -S "$user" 2>/dev/null)
        echo "$STATUS" | tee -a "$TEXT_REPORT" >> "$HTML_REPORT"
        echo "User,Account Status,$STATUS" >> "$CSV_REPORT"
    done < <(getent passwd | awk -F: '$3 >= 1000 {print $1}')
    echo "</pre>" >> "$HTML_REPORT"

    # Available User Roles
    echo "<h3>👥 Available User Roles</h3><pre>" >> "$HTML_REPORT"
    getent group | tee -a "$TEXT_REPORT" >> "$HTML_REPORT"
    echo "</pre>" >> "$HTML_REPORT"

    # Check if MFA is enabled on SSH
    MFA_STATUS="Disabled"
    if grep -q "auth required pam_google_authenticator.so" /etc/pam.d/sshd 2>/dev/null; then
        MFA_STATUS="Enabled"
    fi
    echo "<h3>🔑 MFA Status: $MFA_STATUS</h3>" >> "$HTML_REPORT"
    echo "Security,MFA Status,$MFA_STATUS" >> "$CSV_REPORT"
}

# Run FIO Test
run_fio_test() {
    TEST_NAME=$1
    RW_MODE=$2
    BS_SIZE=$3
    JOBS=$4
    FILE_SIZE=$5

    echo "⚡ Running FIO Test: $TEST_NAME..." | tee -a "$TEXT_REPORT"

    FIO_OUTPUT=$(fio --name="$TEST_NAME" \
        --directory="$FIO_DIR" \
        --ioengine=libaio \
        --rw="$RW_MODE" \
        --bs="$BS_SIZE" \
        --numjobs="$JOBS" \
        --size="$FILE_SIZE" \
        --runtime=30 \
        --time_based \
        --group_reporting \
        --output-format=json)

    echo "$FIO_OUTPUT" > "$JSON_REPORT"

    IOPS_READ=$(echo "$FIO_OUTPUT" | jq '.jobs[0].read.iops' 2>/dev/null)
    IOPS_WRITE=$(echo "$FIO_OUTPUT" | jq '.jobs[0].write.iops' 2>/dev/null)

    echo "<h3>📊 $TEST_NAME</h3><pre>" >> "$HTML_REPORT"
    echo "Read IOPS: $IOPS_READ" >> "$HTML_REPORT"
    echo "Write IOPS: $IOPS_WRITE" >> "$HTML_REPORT"
    echo "</pre>" >> "$HTML_REPORT"

    echo "FIO,$TEST_NAME Read IOPS,$IOPS_READ" >> "$CSV_REPORT"
    echo "FIO,$TEST_NAME Write IOPS,$IOPS_WRITE" >> "$CSV_REPORT"
}

# Run System Check & Security Check
collect_hardware_info
collect_user_security_info

# Run IOPS Tests
echo "<h2>🚀 FIO Benchmarks</h2>" >> "$HTML_REPORT"
run_fio_test "random_read" "randread" "4k" 4 "1G"
run_fio_test "random_write" "randwrite" "4k" 4 "1G"

# Complete HTML File
echo "<h2>📄 Reports</h2>" >> "$HTML_REPORT"
echo "<ul>" >> "$HTML_REPORT"
echo "<li><a href='$TEXT_REPORT'>Text Report</a></li>" >> "$HTML_REPORT"
echo "<li><a href='$JSON_REPORT'>JSON Report</a></li>" >> "$HTML_REPORT"
echo "<li><a href='$CSV_REPORT'>CSV Report</a></li>" >> "$HTML_REPORT"
echo "</ul>" >> "$HTML_REPORT"

echo "<p>✅ Report Generated Successfully!</p></body></html>" >> "$HTML_REPORT"

echo "✅ Reports saved in: $REPORT_DIR"


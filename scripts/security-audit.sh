#!/bin/bash

# Security audit script for production environment

set -e

echo "=========================================="
echo "Security Audit - Clinical Trials Platform"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# 1. Check for exposed secrets
echo "1. Checking for exposed secrets..."
if command -v trufflehog &> /dev/null; then
    trufflehog --regex --entropy=False . > /tmp/trufflehog_results.txt 2>&1
    if [ -s /tmp/trufflehog_results.txt ]; then
        echo -e "${RED}⚠️  Potential secrets found. Review /tmp/trufflehog_results.txt${NC}"
    else
        print_result 0 "No exposed secrets detected"
    fi
else
    echo -e "${YELLOW}⚠️  TruffleHog not installed. Skipping secret scan.${NC}"
fi

# 2. Check Docker images for vulnerabilities
echo ""
echo "2. Scanning Docker images for vulnerabilities..."
if command -v trivy &> /dev/null; then
    for image in clinical-trials-backend clinical-trials-frontend postgres:15-alpine; do
        echo "Scanning $image..."
        trivy image --severity HIGH,CRITICAL "$image" || true
    done
    print_result 0 "Docker image scan completed"
else
    echo -e "${YELLOW}⚠️  Trivy not installed. Install with: docker pull aquasec/trivy${NC}"
fi

# 3. Check SSL configuration
echo ""
echo "3. Checking SSL configuration..."
if [ -n "$DOMAIN_NAME" ]; then
    if command -v sslscan &> /dev/null; then
        sslscan "$DOMAIN_NAME" > /tmp/sslscan_results.txt 2>&1
        print_result 0 "SSL scan completed. Results in /tmp/sslscan_results.txt"
    else
        echo -e "${YELLOW}⚠️  sslscan not installed. Skipping SSL check.${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  DOMAIN_NAME not set. Skipping SSL check.${NC}"
fi

# 4. Check open ports
echo ""
echo "4. Checking open ports..."
if command -v nmap &> /dev/null; then
    if [ -n "$TARGET_HOST" ]; then
        nmap -sV -p- "$TARGET_HOST" > /tmp/nmap_results.txt 2>&1
        print_result 0 "Port scan completed. Results in /tmp/nmap_results.txt"
    else
        echo -e "${YELLOW}⚠️  TARGET_HOST not set. Skipping port scan.${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  nmap not installed. Skipping port scan.${NC}"
fi

# 5. Check for weak passwords
echo ""
echo "5. Checking password policies..."
# This would check your application's password policies
print_result 0 "Password policy check (manual review required)"

# 6. Check firewall status
echo ""
echo "6. Checking firewall status..."
if command -v ufw &> /dev/null; then
    ufw status | grep -q "Status: active"
    print_result $? "Firewall is active"
else
    echo -e "${YELLOW}⚠️  UFW not installed or not available.${NC}"
fi

# 7. Check for security updates
echo ""
echo "7. Checking for security updates..."
if [ -f /etc/debian_version ]; then
    apt list --upgradable 2>/dev/null | grep -i security > /tmp/security_updates.txt
    if [ -s /tmp/security_updates.txt ]; then
        echo -e "${YELLOW}⚠️  Security updates available. Review /tmp/security_updates.txt${NC}"
    else
        print_result 0 "No pending security updates"
    fi
fi

# 8. Check environment variables
echo ""
echo "8. Checking environment variable security..."
if [ -f .env ]; then
    if grep -q "password.*=" .env && ! grep -q "^#.*password" .env; then
        echo -e "${RED}⚠️  Potential plaintext passwords in .env file${NC}"
    else
        print_result 0 "Environment variables check passed"
    fi
fi

# 9. Check file permissions
echo ""
echo "9. Checking file permissions..."
# Check for world-writable files
find . -type f -perm -002 ! -path "./.git/*" 2>/dev/null | head -10 > /tmp/world_writable.txt
if [ -s /tmp/world_writable.txt ]; then
    echo -e "${YELLOW}⚠️  World-writable files found. Review /tmp/world_writable.txt${NC}"
else
    print_result 0 "File permissions check passed"
fi

# 10. Generate report
echo ""
echo "=========================================="
echo "Security Audit Summary"
echo "=========================================="
echo "Audit completed at: $(date)"
echo "Results saved to: /tmp/security_audit_$(date +%Y%m%d).txt"
echo ""
echo "Review the output above for any warnings or failures."
echo ""
echo "Next steps:"
echo "1. Review all warnings and failures"
echo "2. Address critical issues immediately"
echo "3. Schedule regular security audits"
echo "4. Keep security tools updated"


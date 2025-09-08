#!/bin/bash
# One-line deployment script
cd /workspace && rm -rf crm-erp-system && git clone https://github.com/hamidrezasoltanian/hamidreza-soltanian.git crm-erp-system && cd crm-erp-system && chmod +x *.sh && ./full-deploy.sh
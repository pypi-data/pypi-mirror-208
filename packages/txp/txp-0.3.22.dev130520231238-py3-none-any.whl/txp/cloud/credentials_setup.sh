#!/bin/bash
# ------------------------------------------------------------------
# This script will download the secrets configured in Google Secret
# Manager.
#
# Requirements:
#   - GCloud SDK configured.
#   - Granted permissions in the GCloud IAM service for the user authenticated in the GCloud SDK.
#
# ------------------------------------------------------------------

VERSION=0.1.0
SUBJECT=gcloud-gateway-secret-setup
function usage {
    echo "usage: $programname --gateway_key_secret [value] --secret_version [value]"
    echo "  --gateway_key         The secret with the Gateway private key"
    echo "  --secret_version      Secret version for the specified secret"
    exit 1
}

# --- Options processing -------------------------------------------
if [ $# == 0 ] ; then
    usage
    exit 1;
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --gateway_key) gateway_key="$2"; shift; shift ;;
        --secret_version) secret_version="$2"; shift; shift ;;
        *) usage "Unknown parameter passed: $1"; shift; shift;;
    esac;
  done

echo "Secret to download:      $gateway_key"
echo "Specific version:        $secret_version"

# --- DATA -------------------------------------------
service_account_secret_name="cloud-iot-txp-mvp-service-account"
service_account_secret_version="1"

# --- Donwload and saving keys -------------------------------------------

gcloud secrets versions access "$secret_version" --secret="$gateway_key" > rsa_private.pem
gcloud secrets versions access "$service_account_secret_version" --secret="$service_account_secret_name" > service_account.json

# `cloud` Package

This package contains required information and resources to interact with Google Cloud IoT Core.

- `roots.pem`: The Google CA root certificate.
  

- `service_account.json`: The service account JSON key to authenticate the application to GCP. 
**Note:** This file is expected to be found here at runtime. But it's not distributed with the 
  repository sources. See the [credentials setup script](credentials_setup.sh) for more info.
  

- `rsa_private.pem`: The private key for the Gateway running at runtime. **Note:** The private key 
  is expected to be found here at runtime. But they are not distributed with the repository sources. 
  See the [credentials setup script](credentials_setup.sh) for more info.
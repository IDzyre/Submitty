#!/bin/bash
VAGRANT_CLOUD_TOKEN=snLkGsKzUGacZA.atlasv1.Az8EQpaXnY1SMgoef32yHeFAirNtGj6VPeGrQS4LXho3x2ON3ftP6zmK2zfyeqY8pis

VAGRANT_CLOUD_VERSION=$(curl \
  --request GET \
  --header "Authorization: Bearer $VAGRANT_CLOUD_TOKEN" \
  https://app.vagrantup.com/api/v1/box/reapernsgaming/Submitty | \
  python3 -c \
  'import json,sys;obj=json.load(sys.stdin);version = obj["versions"][0]["version"].split(".");version[3] = str(int(version[3])+1);print(".".join(version))')


curl \
  --request POST \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $VAGRANT_CLOUD_TOKEN" \
  https://app.vagrantup.com/api/v1/box/reapernsgaming/Submitty/versions \
  --data "{      'version': {        'version': '$VAGRANT_CLOUD_VERSION',        'description': 'A new version'      }    }"

# # Prepare the provider for upload/get an upload URL

response=$(curl \
    --request GET \
    --header "Authorization: Bearer $VAGRANT_CLOUD_TOKEN" \
    https://app.vagrantup.com/api/v1/box/reapernsgaming/Submitty/version/$VAGRANT_CLOUD_VERSION/provider/virtualbox/upload )
    # python3 -c 'import json,sys;obj=json.load(sys.stdin);print(obj)')


# Extract the upload URL from the response (requires the jq command)

echo $response

# Perform the upload

curl --request PUT "${upload_path}" --upload-file submitty.box

# Release the version

curl \
  --request PUT \
  --header "Authorization: Bearer $VAGRANT_CLOUD_TOKEN" \
   https://app.vagrantup.com/api/v1/box/reapernsgaming/Submitty/version/$VAGRANT_CLOUD_VERSION/release


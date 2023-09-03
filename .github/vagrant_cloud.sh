#!
VAGRANT_CLOUD_TOKEN=snLkGsKzUGacZA.atlasv1.Az8EQpaXnY1SMgoef32yHeFAirNtGj6VPeGrQS4LXho3x2ON3ftP6zmK2zfyeqY8pis
VAGRANT_CLOUD_VERSION=$(git describe --tags)
 
curl \
  --request POST \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $VAGRANT_CLOUD_TOKEN" \
  https://app.vagrantup.com/api/v1/box/myuser/test/versions \
  --data '{ "version": { "version": $VAGRANT_CLOUD_VERSION } }'

# Prepare the provider for upload/get an upload URL

response=$(curl \
    --request GET \
    --header "Authorization: Bearer $VAGRANT_CLOUD_TOKEN" \
    https://app.vagrantup.com/api/v1/box/reapernsgaming/Submitty/version/$VAGRANT_CLOUD_VERSION/provider/virtualbox/upload)

# Extract the upload URL from the response (requires the jq command)

upload_path=$(echo "$response" | jq .upload_path)

# Perform the upload

curl --request PUT "${upload_path}" --upload-file submitty.box

# Release the version

curl \
  --request PUT \
  --header "Authorization: Bearer $VAGRANT_CLOUD_TOKEN" \
   https://app.vagrantup.com/api/v1/box/reapernsgaming/Submitty/version/$VAGRANT_CLOUD_VERSION/release


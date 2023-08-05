# create a machine. For building dockers, consider setting it with a 100GB drive.
# in firewall setting ,allow tcp:22 port access to the office IP and your home's IP.
sudo apt-get update
sudo apt-get install git
sudo apt-get update && sudo apt-get --only-upgrade install kubectl google-cloud-sdk-firestore-emulator google-cloud-sdk-datastore-emulator google-cloud-sdk-kpt google-cloud-sdk-spanner-emulator google-cloud-sdk-anthos-auth google-cloud-sdk-app-engine-python-extras google-cloud-sdk-kind google-cloud-sdk-cloud-build-local google-cloud-sdk-app-engine-python google-cloud-sdk-app-engine-java google-cloud-sdk-pubsub-emulator google-cloud-sdk-app-engine-grpc google-cloud-sdk-app-engine-go google-cloud-sdk-skaffold google-cloud-sdk google-cloud-sdk-bigtable-emulator google-cloud-sdk-datalab google-cloud-sdk-minikube google-cloud-sdk-cbt
export REPO_NAME=py-sigparser
gcloud source repos clone py-sigparser
cd py-sigparser/
git init
git remote
git pull origin service_setup
# setup docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker noam_mansovsky_zoominfo_com
echo Please log out an login again to finish docker setup
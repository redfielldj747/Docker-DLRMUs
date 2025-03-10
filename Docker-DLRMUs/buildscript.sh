if [ -x "$(command -v docker)" ]; then
    echo "Docker is installed, creating dlrmus docker images"
    # command
else
    echo "Install docker and generate at least the hello world container"
    # command
fi
sleep 3

docker image build -t dlrmus_query -f ./dlrmus_query .
docker image build -t dlrmus_update -f ./dlrmus_update .

docker volume create dlrmus

cp -r ./dlrmus/* /var/lib/docker/volumes/dlrmus/_data/

mkdir -p generated
docker build .
docker run --rm -it -v ./generated:/out $(docker build -q .)

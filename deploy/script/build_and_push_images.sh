#!/bin/sh

set -exu

TAG=${1-latest}
IMGNAME=${2}
REPO=934833258096.dkr.ecr.eu-west-2.amazonaws.com
DIR=.

# ecr-password must be there.
docker login -u AWS --password-stdin $REPO < ecr-password

docker pull $REPO/$IMGNAME:latest-runtime || true
docker pull $REPO/$IMGNAME:latest-assetbuilder || true

docker build \
    --target assetbuilder \
    --cache-from=$REPO/$IMGNAME:latest-assetbuilder  \
    --tag $REPO/$IMGNAME:latest-assetbuilder \
    -f deploy/django/Dockerfile \
    $DIR

docker push $REPO/$IMGNAME:latest-assetbuilder

docker build \
    --target runtime \
    --build-arg COMMIT_ID=$TAG \
    --cache-from=$REPO/$IMGNAME:latest-runtime \
    --cache-from=$REPO/$IMGNAME:latest-assetbuilder  \
    --tag $REPO/$IMGNAME:$TAG \
    --tag $REPO/$IMGNAME:latest-runtime \
    -f deploy/django/Dockerfile \
    $DIR

docker push $REPO/$IMGNAME:latest-runtime
docker push $REPO/$IMGNAME:$TAG

echo "Done."

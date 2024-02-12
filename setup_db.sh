#!/bin/bash

# Start local PostGIS container
# docker run -it --rm --name pg-bem --net host -v $PWD/pg-data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres -e POSTGRES_USER=postgres -e POSTGRES_DB=dj_bem -d postgis/postgis:16-3.4

# Setup tunnel to remote pg cluster
ssh ssh0a.prod.bgdi.ch -L 15432:pg-geodata-replica.bgdi.ch:5432

# MESHCARD API

This is an API for handling meshcards for helping the operation of data meshes. This is meant to be deployed as an image to a data mesh or data commons.

## Endpoints

### GET /meshcard/nodecard
Get all node cards in a system

### POST /meshcard/nodecard
With a body of a node card json this validates the node card against the mesh card and adds it to the mesh system and into the mesh card.

### POST /meshcard/nodecard/validate
With a body of node card json validate the node card agains the mesh card.

### GET /meshcard/nodecard/{node-id}
Get specified {node-id} node card

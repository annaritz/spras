## Contributing Guide Notes

# Step 0

- "An alternative way to set up SPRAS..." a little clunky for new folks.
- I think the end of this step needs to have a summary about the structure of the code repository, or walks contributors through it.

# Step 1

- Typo in the pre-formatted text.
- Explain why you need to copy the inputs to this directory. It's to run the docker image locally.
- To run `local_neighborhood_alg.py` on the inputs:
```
cp ../../test/LocalNeighborhood/input/ln-network.txt .
cp ../../test/LocalNeighborhood/input/ln-nodes.txt .
python local_neighborhood_alg.py --network ln-network.txt --nodes ln-nodes.txt --output ln-out.txt
```
- To compare the output with the existing output:
```
cat ln-out.txt
cat ../../test/LocalNeighborhood/expected_output/ln-output.txt
diff ln-out.txt ../../test/LocalNeighborhood/expected_output/ln-output.txt
```

# Step 2

- Complete the Dockerfile needs more information, and it seems to lead users astray with the Python image and suggested Dockerfiles.
- The Dockerfile needs more guidance.
  - What should the working directory be named?
  - Do you need anything other than the single alpine line?
  - PathLInker includes a line from the All of Us project - is that necessary?
  - How do you copy files?
- Build the docker image. First open Docker Desktop (I think you need that running). Need to add tag (latest? v1? etc.).
 ```
 docker build -t annaritz/local-neighborhood -f Dockerfile .
 ```
- Docker run command needs more instructions:
```
docker run -w /data --mount type=bind,source=/Users/aritz/Documents/github/projects/annaritz-spras/docker-wrappers/LocalNeighborhood,target=/data annaritz/local-neighborhood python local_neighborhood_alg.py --network /data/ln-network.txt --nodes /data/ln-nodes.txt --output /data/ln-output.txt
```
- Alternative:
```
docker run -v /Users/aritz/Documents/github/projects/annaritz-spras/test/LocalNeighborhood/input:/input -v /Users/aritz/Documents/github/projects/annaritz-spras/docker-wrappers/LocalNeighborhood:/output annaritz/local-neighborhood python local_neighborhood_alg.py --network /input/ln-network.txt --nodes /input/ln-nodes.txt --output /output/ln-out.txt
```
- Go to docker desktop and see it running. Also include instructions for stopping the container when you are done testing.
- Docker login:
```
docker login
```
- Docker push
```
docker push annaritz/local-neighborhood
```
- Go to dockerhub and see it. https://hub.docker.com/repository/docker/annaritz/local-neighborhood

# Step 3

- What are the possible required inputs? `nodetypes` vs. `nodes`?
- How do you test `local_neighborhood.py` while you work through Step 3?
- " In an interactive Python session, run the following commands to load the data0 dataset and explore the nodes and interactome." - this has to happen at the top level of the repo.

```
>>> from spras.config.dataset import DatasetSchema
>>> dataset_params = DatasetSchema(**dataset_dict)
>>> print(dataset_params)
label='data0' node_files=['node-prizes.txt', 'sources.txt', 'targets.txt'] edge_files=['network.txt'] other_files=[] data_dir='input'
>>> data = Dataset(dataset_params)
>>> data.node_table.head()
  NODEID  prize active dummy sources targets
0      C    5.7   True   NaN     NaN    True
1      B    NaN    NaN   NaN     NaN     NaN
2      A    2.0   True  True    True     NaN
>>> data.interactome.head()
  Interactor1 Interactor2  Weight Direction
0           A           B    0.98         U
1           B           C    0.77         U
```
- need to specify that LocalNeighborhood requires an **undirected** interactome.

# Step 4

- Make a new config with just LocalNeighborhood.
```
cp config/config.yaml config/contrib.yaml
# make the suggested changes
snakemake --cores 1 --configfile config/contrib.yaml
```

- YAML name: underscores/spaces ok?
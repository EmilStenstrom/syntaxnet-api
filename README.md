A Dockerfile that helps you get Syntaxnet DRAGNN working, with a json api powered by falcon.

Here's how you get everything running:

1. **Download the pretrained model files**

    Download this file from Google Drive:
    https://drive.google.com/uc?id=0BxpbZGYVZsEeSFdrUnBNMUp1YzQ&export=download

    Unzip it into a directory where you want your model stored.

2. **Start the server**

    Save this to a file called `rebuild-and-run.sh`, changing things to fit your environment (see below):

    ```bash
    #!/bin/bash
    docker build --rm -t syntaxnet-api -f Dockerfile .

    # :ro at the end of -v makes volume read-only
    docker run --rm -p 8000:80 -v ~/Projects/conll17-dragnn/:/usr/local/tfmodels:ro -e LANGUAGE="Swedish" syntaxnet-api
    ```

    * **syntaxnet-api** is the name of the container
    * **8000** is the port where the API will be exposed
    * **~/Projects/conll17-dragnn/** is the directory where you unziped the model files
    * **/usr/local/tfmodels** is the directory inside the container (don't change this)
    * **-e LANGUAGE="Swedish"** is the name of the directory where the files for your language resides

    Make it runnable: `chmod +x rebuild-and-run.sh`

    Now run it: `./rebuild-and-run.sh`

    This will start a falcon server that runs on port 8000.

3. **Use the API**

    The API can be used from any program that can send HTTP requests and parse JSON. Here's how you would send data to it using plain curl from the command line:

    ```bash
    curl -i -XPOST --data-urlencode "data=Detta är en mening." http://localhost:8000 && echo ""
    ```


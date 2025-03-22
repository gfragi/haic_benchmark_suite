# Node-RED integration with HAIC and KubeFlow

PROPER README TO BE ADDED, NOTES FOLLOW:

## Generate Client Code from OpenAPI Specifications

Code generation (from within the dev Node-RED container) for clients to HAIC and KubeFlow APIs:

```bash
# From home directory, in the dev container
npm install -D openapi-typescript-codegen
npx openapi-typescript-codegen   --input /data/openapi_integration/KubeFlow_OpenAPI_3_converted.yaml --output /data/api_clients/kubeflow_client/   --exportSchemas true
npx openapi-typescript-codegen   --input /data/openapi_integration/HAIC_OpenAPI.yaml --output /data/api_clients/haic_client/   --exportSchemas true
```

## To initialize Node-RED and run it properly

1. Start the Node-RED container
2. Use bash into the container and do the following to have the client code compiled from TypeScript to JavaScript:

    ```bash
    npm install --save-dev typescript
    npx tsc --init
    cd /data/api_clients/haic_client/
    tsc --outDir ./dist --target  es2016 ./**/*.ts *.ts --module commonjs
    cd /data/api_clients/kubeflow_client/
    tsc --outDir ./dist --target  es2016 ./**/*.ts *.ts --module commonjs
    ```

3. Install dependencies of Node-RED

    ```bash
    cd /data/
    npm install
    ```

4. Restart the Node-RED container

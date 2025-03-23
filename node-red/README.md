# Node-RED integration with HAIC and KubeFlow

PROPER README TO BE ADDED, NOTES FOLLOW:

- Check following subsections, follow the instructions!
- The `.env` file based on the example from the `backend` directory, has to be both in the `backend` and the project root directory!
  - Required for the `dev.docker-compose.yml` to work properly!
- Copy the `example.*` files in the `node-red` directory within the same place without the `example.` prefix!
  - Make sure to **comment out the functionGlobalContext section from settings.js**, then do the steps in the subsections using the compose file, and then uncomment it back and restart the Node-RED container!

PROPER PREPARATION AND PACKAGING OF THE HumAIne NODE-RED CONTAINER TO BE ADDED LATER, based on the development notes!

## Generate Client Code from OpenAPI Specifications

This step is required to generate the client code for the APIs of HAIC and KubeFlow, **if there are changes in the target API**, so that it is used in Node-RED later.
Skip this step if the API specifications are not changed, as the generated client code is already included in the repository. This step is not part of the Node-RED container creation, it is only only to be used in development.
Code generation (from within the dev Node-RED container) for clients to HAIC and KubeFlow APIs:

```bash
# From home directory, in the dev container
npm install -D openapi-typescript-codegen
npx openapi-typescript-codegen   --input /data/openapi_integration/KubeFlow_OpenAPI_3_converted.yaml --output /data/api_clients/kubeflow_client/   --exportSchemas true
npx openapi-typescript-codegen   --input /data/openapi_integration/HAIC_OpenAPI.yaml --output /data/api_clients/haic_client/   --exportSchemas true
```

### Notes for Node-RED usage of TypeScript

IF TYPESCRIPT IS TO BE USED IN THE FINAL NODE-RED INTEGRATIONS FOR HumAIne, HERE ARE SOME OPTIONS TO CONSIDER:

1. Using `node-red-contrib-typescript-node`
This library allows you to write Node-RED nodes using TypeScript. It provides a wrapper around Node-RED's core functionality, enabling you to extend the `Node` class and use TypeScript type definitions. However, it is still in its early stages, so caution is advised when using it[1].

2. `node-red-node-typescript-starter` Template
This GitHub repository offers a quick-start template for creating Node-RED node sets in TypeScript. It includes a structured project setup with TypeScript configuration files (`tsconfig.json`) and build tools (e.g., Rollup). You can scaffold new nodes, develop them in TypeScript, and compile them for use in Node-RED. This approach supports incremental builds and testing during development[2].

3. `node-red-contrib-typescript-template`
This project provides another template for creating Node-RED nodes in TypeScript. It includes example nodes demonstrating how to set up TypeScript-based custom nodes with proper integration into Node-RED[3].

4. Manual Compilation and Integration
If you prefer not to use templates or libraries, you can manually create custom nodes by writing them in TypeScript, compiling them into JavaScript using tools like `tsc`, and packaging them as Node.js modules for Node-RED. This method requires creating both runtime (`*.js`) and editor (`*.html`) files for each node[4].

## To initialize Node-RED and run it properly

Steps to initialize the Node-RED container and run it properly, for development, in the current state:

1. Start the Node-RED container
2. Use bash into the container and do the following to install dependencies of Node-RED

    ```bash
    cd /data/
    npm install
    ```

3. Use bash into the container and do the following to have the client code compiled from TypeScript to JavaScript:

    ```bash
    cd ~
    npm install --save-dev typescript
    npx tsc --init
    cd /data/api_clients/haic_client/
    tsc --outDir ./dist --target  es2016 ./**/*.ts *.ts --module commonjs
    cd /data/api_clients/kubeflow_client/
    tsc --outDir ./dist --target  es2016 ./**/*.ts *.ts --module commonjs
    ```

4. Restart the Node-RED container, after making sure that the `example.*` files are copied to the same directory without the `example.` prefix!

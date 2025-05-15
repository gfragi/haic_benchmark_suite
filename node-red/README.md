# Node-RED integration with HAIC and KubeFlow

PROPER README TO BE ADDED, NOTES FOLLOW:

- Check following subsections, follow the instructions!
- The `.env` file based on the example from the `backend` directory, has to be both in the `backend` and the project root directory!
  - Required for the `dev.docker-compose.yml` to work properly!
- Copy the `example.*` files in the `node-red` directory within the same place without the `example.` prefix!
  - Make sure to **comment out the functionGlobalContext section from settings.js**, then do the steps in the subsections using the compose file, and then uncomment it back and restart the Node-RED container!

PROPER PREPARATION AND PACKAGING OF THE HumAIne NODE-RED CONTAINER TO BE ADDED LATER, based on the development notes!

For the integration, the OpenAPI files that are used to generate the API clients are kept in the repository as reference, in the `node-red/openapi_integration` directory.
THERE ARE TWO APPROACHES FOR API INTEGRATION, BASED ON OPENAPI SPECS, TO BE EVALUATED DURING IMPLEMENTATION, AND THE BEST ONE TO BE USED IN THE FINAL VERSION!

## To initialize Node-RED and run it properly

Steps to initialize the Node-RED container and run it properly, for development, in the current state:

1. Start the Node-RED container
2. Use bash in to the container and do the following to have the custom packages built and prepared for installation, including the custom icons package, and the custom clients for HAIC and KubeFlow:

    ```bash
    cd /data/node-red-contrib-custom-icons/
    npm pack
    cd /data/human_ai_benchmark_suite
    npm install
    npm run build
    npm pack
    cd /data/kubeflow_pipelines_api
    npm install
    npm run build
    npm pack
    ```

    NOTE: If the Swagger codegen approach is not used, the client code for HAIC and KubeFlow will be generated using the openapi-typescript-codegen npm package, and the steps for that are to be followed, and the corresponding steps here will be removed!

3. Use bash into the container and do the following to install dependencies of Node-RED

    ```bash
    cd /data/
    npm install
    ```

4. Use bash into the container and do the following to have the client code compiled from TypeScript to JavaScript:

    ```bash
    cd ~
    npm install --save-dev typescript
    npx tsc --init
    cd /data/api_clients/haic_client/
    tsc --outDir ./dist --target  es2016 ./**/*.ts *.ts --module commonjs
    cd /data/api_clients/kubeflow_client/
    tsc --outDir ./dist --target  es2016 ./**/*.ts *.ts --module commonjs
    ```

    NOTE: Use these versions of the clients if the swagger codegen versions are not working properly! If the swagger codegen versions are working properly, then this step will be removed!

5. Restart the Node-RED container, after making sure that the `example.*` files are copied to the same directory without the `example.` prefix!

## Generate Client Code from OpenAPI Specifications

Choose between the different approaches. Use both during development, if needed, in order to evaluate the best approach, and remove the other.

### Approach 1: Local generation using openapi-typescript-codegen npm package

This step is required to generate the client code for the APIs of HAIC and KubeFlow, **if there are changes in the target API**, so that it is used in Node-RED later.
Skip this step if the API specifications are not changed, as the generated client code is already included in the repository. This step is not part of the Node-RED container creation, it is only only to be used in development.
Code generation (from within the dev Node-RED container) for clients to HAIC and KubeFlow APIs:

```bash
# From home directory, in the dev container
npm install -D openapi-typescript-codegen
npx openapi-typescript-codegen   --input /data/openapi_integration/KubeFlow_OpenAPI_3_converted.yaml --output /data/api_clients/kubeflow_client/   --exportSchemas true
npx openapi-typescript-codegen   --input /data/openapi_integration/HAIC_OpenAPI.yaml --output /data/api_clients/haic_client/   --exportSchemas true
```

In order for this code to be included, the settings.js file needs to have the following lines added to the functionGlobalContext section:

```javascript
        HaicClient: require('./api_clients/haic_client/dist'),
        KubeFlowClient: require('./api_clients/kubeflow_client/dist'),
```

### Approach 2: Using Swagger Codegen

1. Use an external tool, swagger-codegen CLI (or the web version included in swagger editor), to generate the client code for the APIs of HAIC and KubeFlow. This step is not part of the Node-RED container creation. Instead the generated client code is included in the repository. This step is only to be used in development. The type of output selected for swagger codegen is `typescript-axios`. The generated client code is included in the `human_ai_benchmark_suite` and `kubeflow_pipelines_api` directories.

    - In order to generate the client code, use the following command in the  directory where the codegen itself is installed:

    ```bash
    ./run-in-docker.sh generate -i HAIC_OpenAPI.yaml -l typescript-axios -o /gen/out/human_ai_benchmark_suite -DpackageName=human_ai_benchmark_suite
    ```

2. Make sure that for each of the generated, the `package.json` file has the correct version number, the same name as the corresponding directory, and that the `main` field points to the correct file.

3. Change the typescript compilation targets for the generated code, to be compatible with Node.js, and Node-RED by extension. To do that, copy the `tsconfig.template.json` from the `node-red` directory to the root of the generated client code directories, and rename it to `tsconfig.json`.

4. (Re-)Package and (re-)install the client code in the Node-RED container, if the API specifications are changed. If installation is already done, do `npm uninstall <package-name>` before re-installing each package.

    ```bash
    # IF INSTALLED, remove the old versions of the client code
    cd /data
    npm uninstall human_ai_benchmark_suite
    npm uninstall kubeflow_pipelines_api
    # Build and pack the client code for HAIC and KubeFlow
    cd /data/human_ai_benchmark_suite
    npm install
    npm run build
    npm pack
    cd /data
    npm install /data/human_ai_benchmark_suite/human_ai_benchmark_suite-1.0.0.tgz
    # Repeat the same for KubeFlow
    cd /data/kubeflow_pipelines_api
    npm install
    npm run build
    npm pack
    cd /data
    npm install /data/kubeflow_pipelines_api/kubeflow_pipelines_api-2.4.1.tgz
    ```

    NOTE: CAREFUL TO HAVE THE CORRECT VERSION NUMBERS IN THE CORRESPONDING package.json file and the COMMANDS!

## Notes for Node-RED usage of TypeScript

IF TYPESCRIPT IS TO BE USED IN THE FINAL NODE-RED INTEGRATIONS FOR HumAIne, HERE ARE SOME OPTIONS TO CONSIDER:

1. Using `node-red-contrib-typescript-node`
This library allows you to write Node-RED nodes using TypeScript. It provides a wrapper around Node-RED's core functionality, enabling you to extend the `Node` class and use TypeScript type definitions. However, it is still in its early stages, so caution is advised when using it.

2. `node-red-node-typescript-starter` Template
This GitHub repository offers a quick-start template for creating Node-RED node sets in TypeScript. It includes a structured project setup with TypeScript configuration files (`tsconfig.json`) and build tools (e.g., Rollup). You can scaffold new nodes, develop them in TypeScript, and compile them for use in Node-RED. This approach supports incremental builds and testing during development.

3. `node-red-contrib-typescript-template`
This project provides another template for creating Node-RED nodes in TypeScript. It includes example nodes demonstrating how to set up TypeScript-based custom nodes with proper integration into Node-RED.

4. Manual Compilation and Integration.
If you prefer not to use templates or libraries, you can manually create custom nodes by writing them in TypeScript, compiling them into JavaScript using tools like `tsc`, and packaging them as Node.js modules for Node-RED. This method requires creating both runtime (`*.js`) and editor (`*.html`) files for each node.

## Install any local custom npm package into Node-RED

The custom icons package is used as a rudimentary example. All is done by using bash within the Node-RED container:

```bash
cd /data/node-red-contrib-custom-icons/
npm pack
cd /data/
npm install /data/node-red-contrib-custom-icons/node-red-contrib-custom-icons-1.0.0.tgz
```

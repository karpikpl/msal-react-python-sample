# About

React SPA from [Azure Samples](https://github.com/Azure-Samples/ms-identity-docs-code-javascript.git) and Python Django API sample with MSAL.

## Setup

This sample requires two app registrations done in Entra, one for the SPA and one for the API project.

### API App Registration

Create an app registration in Entra without a redirect URL.
Use the "Expose an API" blade to create Application ID URI and register one scope called `onBehalfOfUser`.

In the "Certificates and Secrets" blade add one secret and note the value.

Note the values for `API ID URI`, `Application (client) ID`, `Directory (tenant) ID` and value of the client secret, they will be used in the API project configuration.

### SPA App Registration

Create an app registration in Entra, select "Single Page Application (SPA)" and provide redirect URL of `http://localhost:3000`.

Go to "API permissions" blade and select "Add Permission". From "My APIs" or "APIs my organization uses" find the API app registration - select the `onBehalfOfUser` scope.

Grant admin consent for the selected scope.

Note the values for `Application (client) ID` and `Directory (tenant) ID`, they will be used in the SPA project configuration.

## How to run

1. Modify `react-spa/src/authConfig.js` by replacing `your_client_id`, `your_tenant_id` and `your_api_id` with correct values.
2. Create an `.env` file in `/api/apiproject` directory based on `.env.sample` file.
3. Start both projects
4. Go to `http://localhost:3000` to initiate the login flow and make API requests.

## Other considerations

Other things to consider that this sample skips for simplicity:
1. Token caching in API project
2. Scope verification in the API project
3. Well known keys caching in JWT validation in the API project
# Continuous Deployment for Investment Report Generator Backend

This document outlines the steps to set up continuous deployment for the Investment Report Generator Backend application using Azure App Service. Continuous deployment allows you to automatically deploy your application whenever changes are made to the codebase, ensuring that the latest version is always live.

## Prerequisites

Before setting up continuous deployment, ensure that you have completed the following:

1. **Azure Account**: You must have an active Azure account with access to Azure App Service.
2. **Version Control System**: Your application code should be hosted in a version control system such as GitHub, Azure DevOps, or Bitbucket.
3. **Configured Azure App Service**: Follow the setup guide in `02-azure-app-service-setup.md` to create and configure your Azure App Service.

## Steps to Set Up Continuous Deployment

### Step 1: Connect Your Repository

1. Navigate to the Azure Portal and select your App Service.
2. In the left sidebar, find and click on **Deployment Center**.
3. Choose your preferred source control option (e.g., GitHub, Azure Repos, Bitbucket).
4. Authenticate and authorize Azure to access your repository.
5. Select the repository and branch you want to deploy from.

### Step 2: Configure Build Settings

1. After connecting your repository, you will be prompted to configure build settings.
2. Choose the appropriate build provider (e.g., GitHub Actions, Azure Pipelines).
3. Configure the build settings according to your project requirements. Ensure that the build process includes installing dependencies and running any necessary build scripts.

### Step 3: Set Up Deployment Triggers

1. In the Deployment Center, configure the deployment triggers to specify when deployments should occur (e.g., on every push to the main branch).
2. Optionally, you can set up manual deployment options if needed.

### Step 4: Review and Finish

1. Review your configuration settings and click **Finish** to set up the continuous deployment pipeline.
2. Azure will create the necessary workflows or pipelines based on your selections.

### Step 5: Monitor Deployments

1. After setting up continuous deployment, you can monitor the deployment status in the Deployment Center.
2. Check for any build or deployment errors and troubleshoot as necessary.

## Conclusion

With continuous deployment set up, your Investment Report Generator Backend application will automatically deploy the latest changes from your version control system to Azure App Service. This streamlines the deployment process and ensures that your application is always up to date. For troubleshooting tips, refer to `04-troubleshooting.md`.
# Azure App Service Setup Guide for Investment Report Generator Backend

This document provides a step-by-step guide to set up the Investment Report Generator Backend application on Azure App Service.

## Step 1: Create an Azure Account

1. Go to the [Azure website](https://azure.microsoft.com/).
2. Click on "Start free" to create a new account.
3. Follow the prompts to complete the registration process. You may need to provide a credit card for verification, but you will not be charged for using the free tier.

## Step 2: Create a Resource Group

1. Log in to the [Azure Portal](https://portal.azure.com/).
2. In the left sidebar, click on "Resource groups."
3. Click on the "+ Create" button.
4. Fill in the required fields:
   - **Subscription**: Select your subscription.
   - **Resource group**: Enter a name for your resource group (e.g., `investment-report-generator-rg`).
   - **Region**: Choose a region close to your user base.
5. Click "Review + create" and then "Create."

## Step 3: Create an App Service

1. In the Azure Portal, click on "App Services" in the left sidebar.
2. Click on the "+ Create" button.
3. Fill in the required fields:
   - **Subscription**: Select your subscription.
   - **Resource group**: Choose the resource group you created earlier.
   - **Name**: Enter a unique name for your app (e.g., `investment-report-generator`).
   - **Publish**: Select "Code."
   - **Runtime stack**: Choose "Python" and select the version compatible with your application (e.g., Python 3.11).
   - **Region**: Select the same region as your resource group.
4. Click "Next" to configure additional settings as needed, then click "Review + create" and finally "Create."

## Step 4: Configure Application Settings

1. Once the App Service is created, navigate to it in the Azure Portal.
2. In the left sidebar, click on "Configuration."
3. Under "Application settings," add the following key-value pairs:
   - `GOOGLE_API_KEY`: Your Google Gemini API key.
   - `TAVILY_API_KEY`: Your Tavily API key (if applicable).
4. Click "Save" to apply the changes.

## Step 5: Deploy the Application

1. In the Azure Portal, navigate to your App Service.
2. In the left sidebar, click on "Deployment Center."
3. Choose your preferred deployment method (e.g., GitHub, Azure Repos, or Local Git).
4. Follow the prompts to connect your repository and configure the deployment settings.
5. Once configured, click "Finish" to set up the deployment.

## Step 6: Access Your Application

1. After deployment is complete, navigate to the URL of your App Service (e.g., `https://investment-report-generator.azurewebsites.net`).
2. You should see the Investment Report Generator Backend application running.

## Conclusion

You have successfully set up the Investment Report Generator Backend application on Azure App Service. For further configurations or troubleshooting, refer to the other documentation files in this project.
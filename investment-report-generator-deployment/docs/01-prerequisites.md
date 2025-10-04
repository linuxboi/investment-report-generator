# Prerequisites for Deploying the Investment Report Generator Backend

Before deploying the Investment Report Generator Backend application on Azure App Service, ensure you have the following prerequisites in place:

## Software Requirements

1. **Python 3.11+**: Ensure that Python is installed on your local machine. The application has been tested with Python 3.13.
   - You can download Python from the official website: [python.org](https://www.python.org/downloads/).

2. **Node.js 18+**: Node.js is required to build the frontend bundle.
   - Download Node.js from the official website: [nodejs.org](https://nodejs.org/).

3. **Git**: Version control system to manage your codebase.
   - Install Git from: [git-scm.com](https://git-scm.com/downloads).

## Azure Account

- **Azure Subscription**: You need an active Azure subscription to create and manage Azure resources.
  - If you don't have an account, you can sign up for a free account at [azure.com](https://azure.microsoft.com/free/).

## Configuration

1. **Google Gemini API Key**: Obtain a Google Gemini API key and ensure it is accessible as `GOOGLE_API_KEY` in your environment variables or in a `.env` file.
   
2. **(Optional) Tavily API Key**: If you wish to unlock extended web research capabilities, obtain a Tavily API key and set it as `TAVILY_API_KEY`.

3. **Database Setup**: Familiarize yourself with SQLite, as the application uses an SQLite database (`reports.db`) to store reports. The database will be created automatically upon the first run.

## Additional Tools

- **Azure CLI**: Install the Azure Command-Line Interface (CLI) for managing Azure resources from the command line.
  - Installation instructions can be found at: [docs.microsoft.com/cli/azure/install-azure-cli](https://docs.microsoft.com/cli/azure/install-azure-cli).

Ensure all the above prerequisites are met before proceeding with the deployment steps outlined in the subsequent documentation.
# Troubleshooting Tips for Investment Report Generator Deployment

This document provides troubleshooting tips and common issues that may arise during the deployment of the Investment Report Generator Backend application on Azure App Service, along with their solutions.

## Common Issues and Solutions

### 1. Application Fails to Start
- **Issue**: The application does not start after deployment.
- **Solution**: Check the application logs in the Azure portal. Look for any errors related to missing environment variables or incorrect configurations. Ensure that all required environment variables (e.g., `GOOGLE_API_KEY`, `TAVILY_API_KEY`) are set correctly in the App Service configuration.

### 2. Database Connection Errors
- **Issue**: The application cannot connect to the SQLite database.
- **Solution**: Ensure that the database file (`reports.db`) is included in the deployment package. If using a different database (e.g., Azure SQL), verify the connection string and ensure that the database is accessible from the App Service.

### 3. Missing Dependencies
- **Issue**: The application throws errors related to missing Python packages.
- **Solution**: Ensure that the `requirements.txt` file is included in the deployment package. Azure App Service should automatically install the dependencies listed in this file. If not, check the deployment logs for any errors during the installation process.

### 4. Frontend Not Loading
- **Issue**: The React frontend does not load or shows a 404 error.
- **Solution**: Verify that the frontend build output is correctly deployed to the `frontend/dist/` directory. Ensure that the Flask server is configured to serve static files from this directory.

### 5. API Endpoint Errors
- **Issue**: API endpoints return 404 or 500 errors.
- **Solution**: Check the routing configuration in the Flask application. Ensure that the API routes are correctly defined and that the Flask server is running without errors. Review the application logs for more details.

### 6. Environment Variable Issues
- **Issue**: The application behaves unexpectedly due to incorrect environment variables.
- **Solution**: Double-check the environment variables set in the Azure App Service configuration. Ensure that they match the expected values and formats as specified in the `.env` file.

### 7. CORS Issues
- **Issue**: Cross-Origin Resource Sharing (CORS) errors when accessing the API from the frontend.
- **Solution**: Configure CORS in the Flask application to allow requests from the frontend domain. This can be done using the `flask-cors` package.

### 8. Performance Issues
- **Issue**: The application is slow or unresponsive.
- **Solution**: Monitor the application performance using Azure Application Insights. Identify any bottlenecks in the code or database queries. Consider scaling the App Service plan if necessary.

## Additional Resources
- Azure App Service Documentation: [Link to Azure Docs](https://docs.microsoft.com/en-us/azure/app-service/)
- Flask Documentation: [Link to Flask Docs](https://flask.palletsprojects.com/)
- Python Package Index: [Link to PyPI](https://pypi.org/)
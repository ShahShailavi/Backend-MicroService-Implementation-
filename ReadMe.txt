#List of members

1. Shailavi Shah
2. Sneha Parikh
3. Tamanna Bhatt

#Project 1 for backend
1. Copy the project1 folder to the working directory.
2. Install needed modules from Requirements.txt file
3. Run Procfile using foreman start to run all the services
4. Run py.test to run all the test cases.

#Note:
1. microservice.db file already has 1st user, and one article inserted into it.
2. In article table, to retrieve articles and all data, we have taken help of article_title and article_title is Unique.
   so when you again run py.test, then it must fail one test case which is post new article because it is already in our database.
3. We have also attached one curl file which lists all the curl commands to test our code for all possible scenario and all edge cases.
4. All curl commands are running on port number 5000.

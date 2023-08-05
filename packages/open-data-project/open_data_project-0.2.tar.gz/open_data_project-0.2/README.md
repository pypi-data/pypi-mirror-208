Open_data_project
=================

Open_data_project contains the back-end of the Open Data Portal Framework.
It provides the data-retrieval scripts, as well as the scripts to manipulate and organize the data in a way to be suitable to export it the open data portal website.
It also provides simple commands to create an open data portal and setting up its whole structure - both for the front-end and the back-end.

# User Manual

1. Open the terminal and navigate to a project folder
2. Run the following command to install the package on your device
```
pip install open_data_project
```

3. Create and set your open data portal structure running the following command, where the "<project_name>" is how you want to call the project folder 
```
odp create <project_name>
```

4. Navigate to the generated back-end folder "od_bods" in your project and open the sources.csv file to add your sources URLs
5. To run the whole workflow, which include the collection of the datasets and their export to the front-end, in terminal run the following command
```
odp run main
```

6. To run the website on a local server, open the terminal, navigate to the generated front-end folder jkan and type the following command
```
bundle exec jekyll serve --watch --incremental
```
This will serve it on a local host. To see it, open the browser and open the "https://localhost:4000/jkan" 

7. To make use of the automation workflows and deploy your website online, upload your code to GitHub by creating an organization for your open data portal and uploading the back-end and the front-end folders(od_bods and jkan) in different repositories calling them with the same names.
8. Generate personal access tokens and add them as repository secrets for the automation workflows in your back-end repository
9. Deploy your portal's website on GitHub Pages in the settings of your front-end repository


For more information, look at the provided video demonstration and the documentations.

# 364final


**Brief Description**

This application allows a user to search for different Marvel characters and learn information related to that character such as character description and comics that the character is featured in. They can search for characters on the home page (/) which will display the character descriptions and images on the /characters app route. To see the comics that character is in, they can click 'See all comics', which would navigate them to /comics app route. Registered and logged in users can also create comic collections from the available list of comics on the /create_collection app route. After creating a collection, users can view a single collection (/collection/<collection_id>), all of their collections (/collections), and also update any of their existing collections if they'd like (/update/<collection_name>). Similarly, any collection can be deleted by clicking the 'Delete' button of the corresponding collection (/delete/<collection_id>). 

**Link to Heroku**
https://marvel-comics-app.herokuapp.com/

**Requirements**

- [x] Ensure that your SI364final.py file has all the setup (app.config values, import statements, code to run the app if that file is run, etc) necessary to run the Flask application, and the application runs correctly on http://localhost:5000 (and the other routes you set up). Your main file must be called SI364final.py, but of course you may include other files if you need.

- [x] A user should be able to load http://localhost:5000 and see the first page they ought to see on the application.

- [x] Include navigation in base.html with links (using a href tags) that lead to every other page in the application that a user should be able to click on. (e.g. in the lecture examples from the Feb 9 lecture, like this )

- [x] Ensure that all templates in the application inherit (using template inheritance, with extends) from base.html and include at least one additional block.

- [x] Must use user authentication (which should be based on the code you were provided to do this e.g. in HW4).

- [x] Must have data associated with a user and at least 2 routes besides logout that can only be seen by logged-in users.

- [x] At least 3 model classes besides the User class.

- [x] At least one one:many relationship that works properly built between 2 models.

- [x] At least one many:many relationship that works properly built between 2 models.

- [x] Successfully save data to each table.

- [x] Successfully query data from each of your models (so query at least one column, or all data, from every database table you have a model for) and use it to effect in the application (e.g. won't count if you make a query that has no effect on what you see, what is saved, or anything that happens in the app).

- [x] At least one query of data using an .all() method and send the results of that query to a template.

- [x] At least one query of data using a .filter_by(... and show the results of that query directly (e.g. by sending the results to a template) or indirectly (e.g. using the results of the query to make a request to an API or save other data to a table).

- [x] At least one helper function that is not a get_or_create function should be defined and invoked in the application.

- [x] At least two get_or_create functions should be defined and invoked in the application (such that information can be saved without being duplicated / encountering errors).

- [x] At least one error handler for a 404 error and a corresponding template.

- [x] Include at least 4 template .html files in addition to the error handling template files.

- [x] At least one Jinja template for loop and at least two Jinja template conditionals should occur amongst the templates.

- [x] At least one request to a REST API that is based on data submitted in a WTForm OR data accessed in another way online (e.g. scraping with BeautifulSoup that does accord with other involved sites' Terms of Service, etc).

- [x] Your application should use data from a REST API or other source such that the application processes the data in some way and saves some information that came from the source to the database (in some way).

- [x] At least one WTForm that sends data with a GET request to a new page.

- [x] At least one WTForm that sends data with a POST request to the same page. (NOT counting the login or registration forms provided for you in class.)

- [x] At least one WTForm that sends data with a POST request to a new page. (NOT counting the login or registration forms provided for you in class.)

- [x] At least two custom validators for a field in a WTForm, NOT counting the custom validators included in the log in/auth code.

- [x] Include at least one way to update items saved in the database in the application (like in HW5).

- [x] Include at least one way to delete items saved in the database in the application (also like in HW5).

- [x] Include at least one use of redirect.

- [x] Include at least two uses of url_for. (HINT: Likely you'll need to use this several times, really.)

- [x] Have at least 5 view functions that are not included with the code we have provided. (But you may have more!)

- [x] Deploy the application to the internet (Heroku) — only counts if it is up when we grade / you can show proof it is up at a URL and tell us what the URL is in the README. (Heroku deployment as we taught you is 100% free so this will not cost anything.)
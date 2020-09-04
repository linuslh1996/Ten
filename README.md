# Ten

Finding nice restaurants in a town can be a bit of a pain. We have a lot of data and review sites to access, but often are getting drowned in the data, and end up not much wiser then before. The idea behind this project is to, for each town, present the user with 10 carefully selected choices for a restaurant. These restaurants are displayed with big(ish) pictures and a review, so that there is immediately a sense of what to expect from the restaurant. Sure, no user will find every 10 restaurants attractive, but the chance that there is one nice discovery is quite high. And one restaurant is more than enough to have a nice evening!

## Demo

![Demo](Ten_Screencast.gif)

## Implementation

The implementation is very prototyp-y. In the backend, I use the Google Places API and crawl Trip Advisor for data. Then I combine the data from both providers and rank the restaurant based on a simple score system (a combination between review score and number of reviews). This then gets returned to the frontend. Since the query can be quite time consuming (You can make around one Place Detail request every two seconds), I have written a script that calculates the result for the large German towns and stores it in a database. See the `get_data.py` script. To start the backend, start the `start_api.py` script. The frontend can be started with
````
npm start
````

## Future Work

Right now, the calculation of a fresh result for a town needs around 2 minutes. The download of the photos seems to be the bottleneck and probably can be speed up by requesting a smaller sized image from Google. However, I don't see a way to stay at under 30 seconds for one request, since crawling data and using external APIs (with limitations on usage) just takes time. So while it would be really cool to, for _any_ user-input town, respond swiftly, I don't think that this is feasible.

Besides this, the quality of the data can be improved too, by:
- Taking data from other providers into the mix, e.g. Happy Cow
- Instead of displaying a review as "description" for a restaurant, generate the description automatically (possible to some degree with Machine Learning).
- Every image should be a nice looking image with food. That is not the case now because I can't be too picky with the images Google returns (since I only load 3 images from google per restaurant right now), but it would be cool anyway. Recognition of food + a score on the image quality could probably be done with ML, but of course questionable at what quality.

# Musically


Musically is a project developed for users to visualize and play around with [Spotify's API](https://developer.spotify.com/documentation/web-api/).

NOTE: frontend developments is still WIP - excuse the poor design


## Visual flow

First of all, each user has to login with their Spotify account with OAuth

![alt text](https://github.com/agusbegue/musically/blob/master/frontend/static/images/login.png?raw=true)

The user will redirected to Spotify's site and asked to login and authorize access within several required scopes.

Once logged in, the user will have access to the app, and have available the three screens listed in the navigation bar:

1) **Historic**: this section is about artists' historical popularity (an index provided by Spotify). The user can select several artists in the search bar, click *search artists* and the frontend will download the artists' historic data from the database (collected by the [crawler](#the-crawler)) and display it.

![alt text](https://github.com/agusbegue/musically/blob/master/frontend/static/images/historic.png?raw=true)

2) **Playlists**: this section is about the user's playlists. First, the frontend downloads all the playlists owned by the user. After that, the user can select one or several playlists and the audio features for those playlists' tracks (provided by Spotify) will be downloaded and plotted in a boxplot.

![alt text](https://github.com/agusbegue/musically/blob/master/frontend/static/images/playlists.png?raw=true)

3) **Charts**: this section is about the user's streaming information. The app downloads the user information from the API and displays it in a table

![alt text](https://github.com/agusbegue/musically/blob/master/frontend/static/images/charts.png?raw=true)


## The crawler

Spotify's API provides information about the actual state of the tracks and artists, the progress made by each of these is not provided in the API. This is why a crawler was developed to extract every day this varying information about their popularity and ranking in top playlists, and save it in a database.


## Tools used

The app uses frameworks [Django](https://www.djangoproject.com/) for the backend, [React](https://reactjs.org/) for the frontend and [MongoDB](https://www.mongodb.com/) for database.

The app has error reporting via a [Telegram Bots](https://core.telegram.org/bots)


## How to use?

Clone the repository
```bash
git clone https://github.com/agusbegue/realestate-scraper.git
cd realestate-scraper
```

Database
```bash
python manage.py makemigrations
python manage.py migrate
```

Backend
```bash
pip install -r requirements.txt
python manage.py runserver
```

Frontend (on another terminal)
```bash
cd frontend
npm i
npm run dev 
```

You will have your web running so you can access [localhost:8000](http://localhost:8000) and start using it!
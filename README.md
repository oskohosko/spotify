# Spotify Playlist Exploration

In this little project I set myself the task of exploring with various APIs to help create spotify playlist cover images for me.
Beginning with Spotify's, I was able to get individual track info for the first 100 songs in any given playlist. This included audio features such as tempo, danceability and energy amongst other things.
I knew that I needed a bit more than that in order to get a more accurate cover image at the end, so thankfully I discovered that I can get the genres from each artist in my playlist.

After getting that data, I moved on to using Musixmatch's API to grab lyrics for every song. Now on the free version that I am using, I can only access the first 30% of lyrics from each song.
I tested out some things and 30% of the lyrics was enough to suffice. I was limitted to, however, only 2000 API calls per 24h period, which is 20 playlists or tests. 

This got me thinking and I'm still working on this bit at the moment, but a condition was added to make sure that I don't re-run the whole program if I've already gotten the lyrics for songs in a playlist.

Now, after having the lyrics, artist and track data in my dataframe, I learnt how to use OpenAI's API and GPT 3.5 to get the key meanings and themes of each track's lyrics in 5 words.

Once that was done, I was able to summarise all the genres, getting the most commonly occuring ones, get the average values of all the audio features and filtering out the irrelevant ones, and finally using GPT at the end to summarise all the themes of the lyrics into a final 5 words.

Once this was all summarised it was perfect for me to now try to generate an image based on all of this. 

I trialled a bit with Midjourney to see how well it would work (very well on Midjourney) and after using OpenAI's image creator I was very let down. So, maybe I needed to work on my prompt. And after a bit of trial and error I got it to work a bit better.

I'm still working on touching this up but I just wanted to outline how the project went.

In this project I used Python, pandas, Spotify's API, Musixmatch's API and OpenAI's API.

# Try it yourself

If you want to try this yourself you'll need to sign up to get API keys from Spotify, Musixmatch and OpenAI.
I'll drop the links below:

Spotify: https://developer.spotify.com/

Musixmatch: https://developer.musixmatch.com/

OpenAI: https://openai.com/blog/openai-api

Once you have access to the API keys, I'd suggest creating a .env file and copying the variable names I have used in my main.py file when storing the keys.
Or, you can paste the key in place of wherever I use getenv().

It will take a few minutes at first and the output should include 4 url links to all the images created. A .csv file will also be made in the directory showing all of the stats and lyrics of your playlist.

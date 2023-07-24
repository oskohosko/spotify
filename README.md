# Spotify, Musixmatch and OpenAI API Exploration

In this little project I set myself the task of exploring with various APIs to help create spotify playlist cover images for me.
Beginning with Spotify's, I was able to get individual track info for the first 100 songs in any given playlist. This included audio features such as tempo, danceability and energy amongst other things.
I knew that I needed a bit more than that in order to get a more accurate cover image at the end, so thankfully I discovered that I can get the genres from each artist in my playlist.

I used the pandas module in python to help store all of these features and data in a nice and efficient way. It also means that I can save away progress and access it later without having to go through the whole program again.

After getting that data, I moved on to using Musixmatch's API to grab lyrics for every song. Now on the free version that I am using, I can only access the first 30% of lyrics from each song.
I tested out some things and 30% of the lyrics was enough to suffice. I was limited to, however, only 500 lyrics calls, which is ~5 full playlists per day.

This is where the pandas module and .csv files came in handy as I am able to store away the lyrics in the csv files and access them later if I'm wanting to test on the same playlists.

Now, after having the lyrics, artist and track data in my dataframe, I learnt how to use OpenAI's API and GPT 3.5 to get the key meanings and themes of each track's lyrics in 5 words.

Once that was done, I was able to summarise all the genres, getting the most commonly occuring ones, getting the average values of all the audio features and filtering out the irrelevant ones, and finally using GPT at the end to summarise all the themes of the lyrics of the playlist into a final 5 words.

Once this was all summarised it was perfect for me to now try to generate an image based on all of this. 

I messed around with the prompts, with a lot of trial and error trying to get a prompt that effectively combines all of the playlist data I had gathered. I'm sure there are better prompts out there and I reckon my prompt engineering needs some work but I was able to get DALL-E 2 to generate some cool images. Here are a few.

The first batch using DALL-E 2 for my Aussie Indie playlist:
<br>
<p float="left">
  <img src="provincial/img-DuvQzbcyGhJrIZzu4OelWt1E.png" width=100 />
  <img src="provincial/img-FwKy9rDvwLAcnr4mqjw6UHsL.png" width=100 />
  <img src="provincial/img-VefjVTtADjuWEpPQxNXzvxo6.png" width=100 />
  <img src="provincial/img-YoT3H1DR4s2Cd2HIMBNAg2Gk.png" width=100 />
</p>
<br>
Pretty average to be honest. But things worked a bit better for my techno playlist.
<br>
<p float="left">
  <img src="techno/1-2.png" width=100 />
  <img src="techno/2-2.png" width=100 />
  <img src="techno/3-2.png" width=100 />
  <img src="techno/4-2.png" width=100 />
</p>
These, to me, seem a little bit more technoey and worthy of a cover image for a playlist.

After testing out for a while more, I decided to use Midjourney again just to see the comparison. And was there a lot to compare. 
Midjourney's photos are so so much better and while my code still works and can generate photos, I decided to change it up to create a prompt I could simply copy and paste into Midjourney for a better set of photos.

Here are what Midjourney generated for the same Aussie Indie playlist:

<p float="left">
  <img src="provincial/1.png" width=100 />
  <img src="provincial/2.png" width=100 />
  <img src="provincial/3.png" width=100 />
  <img src="provincial/4.png" width=100 />
</p>
<br>
And the same for the techno playlist:
<br>
<p float="left">
  <img src="techno/1.png" width=100 />
  <img src="techno/2.png" width=100 />
  <img src="techno/3.png" width=100 />
  <img src="techno/4.png" width=100 />
</p>
<br>
# Try it

If you want to try this yourself you'll need to sign up to get API keys from Spotify, Musixmatch and OpenAI.
I'll drop the links below:

Spotify: https://developer.spotify.com/

Musixmatch: https://developer.musixmatch.com/

OpenAI: https://openai.com/blog/openai-api

Once you have access to the API keys, I'd suggest creating a .env file and copying the variable names I have used in my main.py file when storing the keys.
Or, you can paste the key in place of wherever I use getenv().

It will take a few minutes at first and the output should include 4 url links to all the images created. A .csv file will also be made in the directory showing all of the stats and lyrics of your playlist.

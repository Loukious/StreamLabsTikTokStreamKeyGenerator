# TikTok Live Stream Key Generator for OBS Studio Using Streamlabs API

## Description
This application is a simple tool that generates a TikTok Live Stream Key for OBS Studio using the Streamlabs API. Streamlabs TikTok LIVE access is required.

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/loukious)


## Features
- Generate TikTok Live Stream Key using Streamlabs API

## Requirements
- Streamlabs TikTok LIVE access. You can request access [here](https://tiktok.com/falcon/live_g/live_access_pc_apply/result/index.html?id=GL6399433079641606942&lang=en-US)
- TikTok account
- Streamlabs installed on your computer and you are logged in with your TikTok account in Streamlabs (optional)

## Download
- Download the latest release from [here](../../releases/latest)

## Usage
1. Run the application.
2. click on the "Load token" button.
3. 
    1. If you have Streamlabs installed on your computer and you are logged in with your TikTok account in Streamlabs, the application will automatically load the token.
    2. If you don't have Streamlabs installed on your computer or you are not logged in with your TikTok account in Streamlabs, you will need to login with your TikTok account in the browser that will open.

4. Select stream title and category.
5. Click on "Save Config" button to save the token, title and category.
6. Click on the "Go Live" button.


## Screenshots

![Screenshot](https://i.imgur.com/XLroKB2.png)

## Output

The script will output:
- **Base stream URL:** The URL needed to connect to the TikTok live stream.
- **Stream key for OBS Studio (or any other streaming app):** Stream key that that you can use in OBS Studio to stream to TikTok.

## FAQ
### I'm getting a `Maximum number of attempts reached. Try again later.` error. What should I do?
This error sometimes occurs when TikTok detects selenium. You can use this [extension](https://chromewebstore.google.com/detail/export-cookie-json-file-f/nmckokihipjgplolmcmjakknndddifde) to export your cookies and import them into the script.
1. Start by installing the above extension in your browser.
2. Log into TikTok in the browser (if not already logged in), then export the cookies using the extension (while being on TikTok's website). 
3. After that, place the file in the same directory as the script and rename it to `cookies.json` then start the app.
### Do I need to have 1k followers to get Streamlabs TikTok LIVE access?
No, you can request access even if you have less than 1k followers.
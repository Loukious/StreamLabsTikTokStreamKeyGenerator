# TikTok Live Stream Key Generator for OBS Studio Using Streamlabs API

## Description
This application is a simple tool that generates a TikTok Live Stream Key for OBS Studio using the Streamlabs API. Streamlabs TikTok LIVE access is required.

## Stream to TikTok directly from OBS

**[Loukious's TikTok extension for OBS-Multi-RTMP](https://github.com/Loukious/obs-multi-rtmp)** lets you manage TikTok streaming inside OBS. Save your Streamlabs token once, or import it from Streamlabs Desktop, then start your LIVE through OBS's normal streaming controls or the **Multiple output** dock.

- **Automatic Streamlabs setup:** the plugin obtains the streaming server and key when you start, with account eligibility feedback and searchable categories.
- **Native LIVE Studio and Android connections:** choose desktop, Camera LIVE, or mobile gaming, with room creation, signing, and stream metadata handled inside OBS.
- **QR login:** sign in with your phone, renew expired codes automatically, and save account-named `cookies_<username>.json` files.
- **Portrait + landscape:** eligible LIVE Studio and Android Camera LIVE accounts can stream dual layouts with independent scenes, resolutions, encoders, and audio settings.
- **OBS 33 support:** the Windows installer uses the new plugin layout and cleans up legacy copies while preserving other plugins and user settings.

**[Download the OBS plugin](https://github.com/Loukious/obs-multi-rtmp/releases/latest)** · **[Setup and requirements](https://github.com/Loukious/obs-multi-rtmp#readme)**

Requires OBS **32.2.1 or newer**. On Windows, use **Installer.exe** or the standard ZIP for OBS **33+**, and **OBS32.zip** for OBS **32.2.1**. Streamlabs connections require Streamlabs TikTok LIVE access. Native LIVE Studio/Android connections require the [RapidAPI signer](https://rapidapi.com/Loukious/api/tiktok-live-studio-api-signer1); dual layout also requires account eligibility.

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
2. click on the "Load from PC" button if you have Streamlabs installed on your computer and you are logged in with your TikTok account in Streamlabs, otherwise click on the "Login from Web" button.
3. Select stream title and category.
4. Click on "Save Config" button to save the token, title and category.
5. Click on the "Go Live" button.


## Screenshots

![Screenshot](https://i.imgur.com/2PSgEQP.png)

## Output

The app will output:
- **Stream URL:** The URL needed to connect to the TikTok live stream.
- **Stream key for OBS Studio (or any other streaming app):** Stream key that that you can use in OBS Studio to stream to TikTok.

## FAQ
### I'm getting you `You can't open the application "***" because it may be damaged or incomplete` error on MacOS. What should I do?
I don't own a Mac so I can't test the app on MacOS but you can try the following:
1. Open Terminal.
2. Run the following command: `xattr -dr com.apple.quarantine /path/to/the/StreamLabsTikTokStreamKeyGenerator.app` (replace `/path/to/the/StreamLabsTikTokStreamKeyGenerator.app` with the path to the app).
3. Try to run the app again.

### I'm getting an error when I try to stream. What should I do?
1. First make sure it's not an issue related to Streamlabs. Try going live using Streamlabs and see if you get the same error.
2. If it's not an issue related to Streamlabs, you can create an issue on GitHub with the error message and a screenshot of the error.
### Do I need to have 1k followers to get Streamlabs TikTok LIVE access?
No, you can request access even if you have less than 1k followers.

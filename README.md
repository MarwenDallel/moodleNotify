# moodleNotify
moodleNotify is a web scraper that notifies users of changes in their grades. It operates as a system app and eliminates the need to periodically check the institution's moodle platform for updates.   
moodleNotify does not use Moodle's [Web service API functions](https://docs.moodle.org/dev/Web_service_API_functions) because not all users have access to their API keys. The creation of API tokens may need to be manually enabled by platform administrators (see [webservice:createtoken](https://docs.moodle.org/400/en/Capabilities/moodle/webservice:createtoken)).

## Getting Started

### Installing

1. Head over to [releases](https://github.com/MarwenDallel/moodleNotify/releases/latest) and download `Installer.exe`.

2. In the installation wizard, when asked for a serial number, enter `CORONA` then proceed to install moodleNotify on your system.

3. On your first launch, moodleNotify will ask you to generate a GitHub API key, this is used to keep the app up to date and automatically fetch new releases from GitHub. Go to [Personal access tokens](https://github.com/settings/tokens) page and generate an API key with the default scopes.

4. Enter your moodle account credentials (only moodle.moodle.tn supported for now)

5. If all the previous steps have been completed successfully, you will see the following system notification

<p align="center">
  <img src="https://user-images.githubusercontent.com/71770363/168377849-038e76ff-2e70-4198-8aa7-8cadd7b50d40.png" alt="moodleNotify enabled">
</p>

## Troubleshooting
If moodleNotify refuses to launch, consider starting it with administrative privileges.    
Before opening any issues, please consider attaching the log available file at `C:\Program Files (x86)\moodleNotify\logs\moodleNotify.log`.

## Known Issues
- Quitting while downloading closes the app ("Check for Updates")
- Session may hang and become unable to send requests

## Enhancements
- [ ] Rewrite HTTP decorators as _Requests_ hooks.

## Disclaimer
This application is not endorsed or affliated with Moodle™. The usage of this application enables you to receive system notifications about changes in your grades by scraping data from a hosted Moodle platform. The software is provided as is and contains material that is protected by Moodle's trademark. The use of the name and logo is in line with the [Allowed uses of "Moodle™"](https://moodle.com/trademarks/).

## Legal Warning
If you plan on releasing a commercial version of this software you need to consider that Moodle logos can only be included in non-commercial software.

## License (MIT)
Copyright (c) 2022 Marwen Dallel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

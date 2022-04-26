### Minor tasks
* Logout user when banned (when remember me is set, user can be banned and still have access to the site for a long time)
* Nice URLs (user id, location id, etc. replaces by string in URL)
* Increase tests coverage (functional, unit)
* Add owner based access (profile edit, location change,...) - buttons should be hidden automatically when no access is available
* Add filtering to location browsing (by area, type,...)
* Add location privacy levels and update access controll per role accordingly
* Add locations export to GPX
* Add export tool for trip planning (select locations and export these to a pdf)
* Add settings to user accound (send emails settings, how many locations to show, default page after login...)
* Disable login after 3 unsuccessful attemps within minute for a while
* Add ability to transform location ownership (both sides must agree)
* Download files with reasonable filenames instead of the UUIDs
* Take upload photo date from exif
* Show nearby objects

### Complex features
* `povrchovka` - select location you will be visiting, set time of expected return and list of contacts to send email/sms/... when you don't confirm you made it out alive
* Events - e.g. Let's dig this mine/repair this,... - people can join the event, comment,...
* Discussion for locations
* Location concepts - simple UI to create location from field, update and save as final location afterwards
* Guess duplicates - inform user there's a location nearby already when creating
* Keep history of location changes, allow reverting
* Find corresponding geofond ID when creating object by GPS (nearby mines) and suggest it.
* Add importer from other sites - Geofond, podzemi.org, archiv.dolovani.cz
* Allow changing order of photos, POIs, documents,... by user
* Rework library feature - uploading books with authors, description,... Books can be viewed in table and referenced in locations or directly added through interface in location

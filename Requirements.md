# Requirements
User levels:
* Non logged users (guest) can only see object marked as public and cannot change anything
* Newly created users (BFU) can see only basic objects, comments and create comments, request object creation,...
* Common users (Accepted by admins) can see more objects and details, can also see new objects requests and can vote for them
* Admins can accept object requests, can directly create objects, can ban any non-admin user, if enough admin vote for BFU, it will be bumped to common user
* Root can bump users to admins

Users:
* New objects must be accepted by site admins before publishing
* Show log book of visits
* Ability to create groups of starred objects (want to visit,... ) and generate a printable list with details
* Admins can accept user registrations
* User can have different ranks for various types of objects (admin on urbex, bfu on mines,...) -> object groups
* Only users who received invitation from other member can register, keep user who invited the user
* User profile with markdown about-me, photo, list of visited objects, comments,...
* When user is not active - show reason message

Objects
* Importance level of the object (assigned by creator, accepted/changed by admin)
* Objects can be public, private (only owner can access or shared-with users) or with importance level filter
* Object description in markdown
* Short description required, optional long description (object history,...)
* Main object GPS position to be shown on map
* Each object can have multiple POIs with short description (parking place, entrance,...) and photos, each can have separate privacy settings (e.g. upper Hrebec mine entrance)
* User can attach files to objects - maps,... Each has description, priviledge level, creator,...
* Object can have photos with description and importance level set (public object photo, private mine map,...)
* Maybe add a photo gallery?
* One photo can be selected as main for object listing, this must be public
* Object can have state assigned - demolished, unaccessible, freely accessible, guarded,...
* Object can have safety level assigned (for children, equipment needed, dangerous,...)
* Tags support - SRT needed, light needed,....
* Log of visits by user, can attach photo and comment, higher rank users can edit the object properties, other only suggest changes
* Keep history of changes?
* Only admin can delete the object, the creator can only make it private
* Keep author and aproving user info
* Show (filtered by type) nearby objects from other databases (geofond,...), provide way to attach these links automatically
* Comments below objects with reply-to (show notifications to related users, creator,...)

Filtering
* User can filter objects by
  - type
  - state
  - safety level
  - tags
  - with photos
  - last visit date
  - visited by me
  - date added,...

Generic
* Ability for higher user levels to create public actions (or filtered to groups) - e.g. get buddies to dig a mine entrance,...
* Dump other data sources - geofond,...
* Show new objects on home screen
* Notifications to users about various events (comments, replies, new objects,...)

# Database tables
Each table contains id column as a primary key

Access levels as
* 0 - public
* 1 - BFU
* 2 - Common user
* 3 - Admin
* 4 - private

Object types, object states, etc. hardcoded for translations

## User
* name
* password
* email
* is_active
* invited_by - user who invited this user to register
* approved_by - user who approved this user to access the data
* is_admin - user is administrator
* created - date of user registration
* last_login - date of last login
* about - markdown user about me text, can add photos (stored locally in folder user/id)

User with ID 0 is root, all initial users were invited by root - tree of invites can be created and whole branch can
be deactivated.

## Permissions
* user id - user that has this permission
* object type - objects related to this permission
* access_level - current access level to this object type
* assigned_by - user that assigned this permission

## Object
* owner - owner of the object (author usually, ownership can be transferred to other user (he has to agree))
* approved_by - user that confirmed object to be published or None if not approved yet
* created_on - Date of creation
* modified_on - Date of last modification
* last_modified_by - user that modified the object recently
* name - object name
* short_description - short textual object description
* description - object description (markdown support)
* type - object type
* state - object state
* lat - latitude
* lon - longitude
* access_level - lowest access level allowed
* title photo - none or id of the title attachement (must be jpg)

Object type E.g.
- mine
- urbex
- tower (can be climbed on)
- camping place

Object state
- demolished
- official tours
- inaccessible (covered mine entrance,...)
- empty
- furnished
- dangerous
- accessible

More granular object state by tags

## Attachements
* object_id
* created_on
* user_id - user who created it
* name
* description
* access_level - lowest access level allowed
* filename

Files stored on server in object_id/filename folder, images in thumbnails and full size,
converted on upload.
TODO Attachements can be tied to visits or POI...

## Tags
* name - tag name

## Tag map
* tag_id
* object_id

Mapping between tags and object, object can have multiple DB records for multiple tags

## external link
* object_id
* name - name of the link object
* url - destination url

links to external pages for given object

## POI
* object_id
* name
* description
* lat
* lon

Point of interrests - parking place, mine entrance,...

## invitations
* hash - random hash identifying this invitation - used in invitation url
* created_by - user that created the invitation
* expires_on - expiration date

Only one user can use the invitation, after registration is done, the invitation
is removed.

## visits
* object_id - object that was visited
* user_id - user who visited the object
* visited_on
* comment

## comments
* user_id
* reply_to - id of the item we are replying to
* comment - comment text
* created_on

## notifications
* user_id - user to notify
* comment_id - response to comment or NULL
* object_id - approved creation/change or NULL
* created_on - when the notification event happened
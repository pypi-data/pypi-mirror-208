# Changelog

# 0.11.4

- Add support for tracking externally-self-paid accommodation.
- Allow attendees to maintain their current accommodation option even if
  they wouldn't be able to select it, themselves.
- Allow accommodation options to include meals.

# 0.11.3

- Fix a crash in registration in 0.11.2.
- Reword instructions and some registration fields.
- Port badges to django-compressor.

# 0.11.2

- Allow Stripe payments to work for invoices when the <html> tag doesn't
  have an explicit lang.
- Track Registrations and Accommodation requests in Queues.
- Add `DEBCONF_REVIEW_FREE_ATTENDEES` to review free registration
  requests.

# 0.11.1

- Include static assets missed in 0.11

# 0.11

- Avoid crashes when exporting minidc sites
- A badger to remind people to collect their bursaries
- Add a --final argument to `badger_travel_reimbursement_reminder`
- Load moment from the main template
- Include dependent-visibility.js for registration form
- Use Debian's eonasdan-bootstrap-datetimepicker in the registration forms

# 0.10.2

- volunteers: drop deprecated python2 compatibility (this enables using this
  app together with Django 3)

# 0.10.1

- move `now` fixture to a shared location
- debconf.view: fix `get_current_slot()` to support start times from previous
  slots

## 0.10

* minidebconf: add phone number and registration type fields

## 0.9

* Upgrade to Django 3
* Replace `django.conf.urls.url` with `django.urls.re_path`
* Replace `ugettext_lazy` with `gettext_lazy`
* .gitlab-ci.yml: test against bullseye

## 0.8

* `test_registration`: use `register_form_factory` to get registration form
* minidebconf: registration: prevent registrations when they are closed
* Add Font Awesome 5
* stylesheet: use Font Awesome instead of Fork Awesome

## 0.7.1

* Minidebconf: Add optional diets and shirt sizes

## 0.7

* Import sponsor code from dc23
* stylesheet: import a "local" stylesheet

## 0.6.10

* Front Desk View: Track issuance of meal vouchers.

## 0.6.9

* `load_schedule_grid`: make creation of break items idempotent

## 0.6.8

* Add `DEBCONF_SKIPPED_MEALS` to avoid needing to serve breakfast on the
  first day.

## 0.6.7

* `load_schedule_grid`: create break items automatically

## 0.6.6

* `load_schedule_grid`: remove hack used for online DebConfs

## 0.6.5

* Fix queryset filtering bugs in badger_outstanding_invoices and
  cancel_unable_travel_without_bursary. Both were considering too many
  attendees.
* Don't issue 0-value invoices in re-invoicing.
* Allow attendees with early accommodation to go through the
  registration form without losing it.

## 0.6.4

* Fix some registration bugs in accommodation options.
* Fix a bug in the content statistics.
* Fix a bug in update_invoice_metadata.
* Fix a timestamp bug in load_schedule_grid.
* Create the video team in create_debconf_groups.
* Handle GUID EventIDs in load_videos.
* Improve the pricing wording around accommodation options.
* Add an export of visa requests.
* Extract and genericise badger_travel_bursaries from examples.
* Make badger_outstanding_invoices usable across events.
* Add a new terminal state for invoices - refunded.
* Add a management command to cancel registrations for attendees who
  didn't receive a travel bursary and selected the "unable" level of
  need.
* Add a management command to issue invoices to attendees who didn't
  receive bursaries.
* Add a management command to automatically reconfirm attendees, where
  possible.
* Add a pair of management commands to request reconfirmation.

## 0.6.3

* Hot-fix for 0.6.2, a bug in the accommodation options.

## 0.6.2

* Prompt bursary applicants to name the city they are travelling from
* badger_unregistered: If a user has multiple accounts, point this out to them
* Add a field to have accommodation options
* Store a breakdown of the invoice in Stripe Metadata

## 0.6.1

* Require agreement for regular testing, if unvaccinated.

## 0.6.0

* Python 3.10 support
* Make the currencies used for billing and bursaries configurable.
* Registration: Add COVID-19 vaccination page.
* Registration: Add a visa page.
* Registration: Fix some bugs in in-person debconfs, introduced in
  online debconf support.

## 0.5.3

* Extend the format for volunteer-tasks.yml

## 0.5.2

* add management command to send talk upload URLs

## 0.5.1

* display shipping addresses in bursary admin
* display "approx" next to the local currency on invoices

## 0.5.0

* schedule: allow filtering slots before a given time
* schedule: allow filtering slots by duration
* schedule: allow fuzzy matching of talk type and venue names
* schedule: make "spread" the default and only supported behavior

## 0.4.0

* load_schedule_grid: automate scheduling of breaks
* load_schedule_grid: load video flag if available
* add management command for automated scheduling
* Add infrastructure for minimal conference websites
  * debconf: move DCScheduleArrived view to register app
  * Provide infra for minimal conference apps
  * schedule: don't validate contiguousness of schedule items
  * minidebconf: add simple registration module
  * minidebconf: add i18n/l10n support
  * Add generic Salsa login
  * Extract home page features from dc20
  * Extract streaming/schedule features from dc20
  * Extract "wafer-debconf.scss" from dc20
  * `is_it_debconf`: fix crash when there is no ScheduleBlock
  * index: improve create/edit homepage controls
  * `context_processors`: always load site metadata
  * MANIFEST: include extra files
  * setup.py: add missing dependency
  * Make it easier to override theme
  * MANIFEST.in: publish .scss files from `debconf.themes.*`
  * .gitlab-ci.yml: run tests
  * debconf.context_processors: consolidate settings in a single function
  * minidebconf: add init_minidc_menu_pages management command
  * debconf.common_settings: get settings from the environment
  * debconf.common_settings: read salsa auth config from environment
  * debconf.context_processors: fix is_it_debconf
  * test_context_processors: fix tests wrt timezone
  * registration: require login
  * debconf.common_settings: provide default value for SANDBOX
  * settings: disable video reviewer for talk submissions
  * stylesheet: add minimal styling for the schedule table
  * schedule: drop "by" before speaker names
  * video player: vendor video.js and necessary plugins
  * Extract video player code from dc20
  * video player: fix mirror detection for current setup
  * video player: reload source on error
  * schedule: stop hiding time column for slots < 15 min
  * Extract now_or_next from dc20
  * Add some basic tests for create_online_service_urls
  * load_videos: concatenate baseurl instead of joining via os.path.join
  * load_videos: normalize leading and trailing slashes
  * load_videos: fix actual object creation/update
  * profile: hide "Submit talk" if submission is closed
  * profile: hide "not registered" warning if registration is closed
  * minidebconf: registration: support GET at /unregister/
  * .gitlab-ci.yml: also install python3-yaml
  * debconf.context_processors: improve readability
  * debconf.common_settings: take advantage of GeoIP redirector
  * debconf: profile: avoid crash when not using badges app
  * register.urls: fix import of DCScheduleArrived
  * .gitlab-ci.yml: add JS/CSS packages
  * setup.py: add new dependency: django_extensions
  * LICENSE: account for embedded copies files
  * setup: require wafer >= 0.11
  * ci: install dependencies witih pip
  * debconf.common_settings: drop deprecated `safe_mode` option for markitup

## 0.3.20

* invoice: display `DEBCONF_INVOICE_ADDRESS`

## 0.3.19

* Display shipping addresses in Attendee admin views
* Show totals for t-shirt and shoes in statistics

## 0.3.18

* Remove debconf.markdown, taken over by `mdx_staticfiles`
* remove dead code
* talk urls: use TalkUrl.public attribute from newer wafer

## 0.3.17

* talk: display language
* Remove wafer.schedule/venue.html override, not needed
* Describe the exports app

## 0.3.16

* Allow anonymous access to registration statistics.
* Build our public views into django-bakery static builds.
* Hide provisionally-accepted talks from public view, on user profiles.
* Fix rendering of talk edit pages, with django-markitup >= 3.7.
* Move the AoE explanation to `<abbr>`s
* Log shipping addresses during registration.

## 0.3.15

* Add `DEBCONF_INVOICE_ADDRESS` setting.
* Break up Shipping Address into separate fields.
* Make deadlines AoE.

## 0.3.14

* `badger_speakers_scheduled`: allow to mail speakers a second time
* `load_videos`: conform to the new sreview output format
* `load_videos`: overwrite videos

## 0.3.13

* Bug fixes to schedule timezone and volunteer permissions.

## 0.3.12

* Put auth on the volunteer views, so anonymous users get sent to log
  in, rather than 500ing.

## 0.3.11

* Volunteer tools:
  - Bug fixes for the volunteer timezone support.
  - Add a `required_permission` property to tasks.
  - Add a `task.accept_video_tasks` permission.

## 0.3.10

* Volunteer tools:
  - Allow importing video volunteer tasks from YAML, together with the
    ad-hoc tasks.
  - Display Volunteer views in the Volunteer's configured timezone.

## 0.3.9

* Tools for generating Jitsi, Etherpad, etc. URLs.

## 0.3.8

* schedule: improve navigation in single-day schedule pages.

## 0.3.7

* several improvements in the schedule:
  * drop track sidebar
  * improve display of local time
  * make video/no-video icon a bit smaller
  * add class to Time header cell to allow styling
  * add fullscreen mode

## 0.3.6

* generalize `badger_speakers_scheduled` to work for all future conferences.

## 0.3.5

* `load_schedule_grid`: schedule activities past midnight
* Add command to print a list of countries by talks, with notes

## 0.3.4

* Only look up the payment intent for new invoices
* bursary admin: list name and email

## 0.3.3

* Minor:
  * T-shirt instructions and help text.

## 0.3.2

* Minor:
  * Only mention expense bursaries, for online DebConfs, in confirmation
    emails, and the profile page.
  * Set registration completed timestamps.
  * Correctly determine registration completion in statistics, for
    online debconfs.
  * Render Kosovo, in country listings.
  * Include expense bursaries in admin views, statistics, exports.
  * Collect shipping addresses for online debconfs.

## 0.3.1

* Render invoices gracefully without Stripe credentials
* Add an event type breakdown to the content statistics

## 0.3.0

* Major changes:
  * Support DebConf Online (stripped down registration)
  * Replace PayPal payments with Stripe
* Bug fixes:
  * Avoid duplicating invoices when the total hasn't changed.

## 0.2.1

* Bug fixes:
  * Support anonymous views of the closed registration page
  * Drop unused imports
  * Drop use of six, we're py3k-only, baby
  * Fix volunteer statistics
  * Allow content statistics to render without a schedule
  * In Wafer > 0.7.7 slots have datetime fenceposts
  * Merge wafer.schedule templates from wafer 0.9.0
  * Django 2 compatibility: `is_authenticated` -> bool
  * Don't blow up if an event lost a venue
  * Fix volunteer admin
* Minor behavior changes:
  * Allow Content Admin to view users

## 0.2.0

* Port to Django 2:
  * Set `on_delete` on Foreign Keys
  * django.core.urlresolvers was renamed to django.urls in 1.10
  * Migration to update the bursaryreferee FK
* Port to wafer 0.9.0
  * debconf.views: fix against latest wafer >= 0.7.7
  * Update `load_schedule_grid` to support blocks
  * Make slot times TZ aware

## 0.1.22

* Move prices to a settings PRICES dict.

## 0.1.21

* Fix a bug in the bursary status, after DebConf has started.
* Add an invoice export.
* Add video player to talk pages.
* Simplify the volunteer task mapping data model.
* Mention the video team's advice for presenters, in the talk acceptance
  email.
* Add statistics pages for Volunteers and Content.
* Expose arrived and departed state to DCSchedule.
* Include Checked In state in bursary exports.
* Update the reimbursement email, to match current SPI requirements.

## 0.1.20

* UNKNOWN

## 0.1.19

* Support Conference Dinner in FD meal sales.
* Boldly show paid status in FD check-in.
* Set a deadline by which bursaries have to be approved, after which
  the user can be invoiced.
* Fail gracefully when a talk doesn't have a track (in the colouring
  code)
* Disable retroactive volunteering.

## 0.1.18

* More tweaks to video volunteer wrangling.

## 0.1.17

* Improve volunteer signup.
* Automate Video Team T-Shirt distribution.

## 0.1.16

* createtasks: load task template descriptions

## 0.1.15

* Add timestamps to Attendee's registration.
* Show if attendees registered late, in front desk.

## 0.1.14

* Allow volunteers to set their preferences.
* Return a 404 when a non-registered user tries to preview a badge.

## 0.1.13

* Support Postgres in the queue migration from 0.1.12

## 0.1.12

* Add a management command to create volunteer tasks from YAML
* Improve the track list in the schedule.
* Change registration permissions (only admins can take cash).
* Get badges working again.
* Assign keysigning IDs, and add a management command to sort them.

## 0.1.11

* Generalize the badger speaker script to all talk statuses.
* Add a keysigning export.

## 0.1.10

* Validate speaker attendance dates, when schedule editing.
* Use DebConf's custom schedule templates.
* Add Python 3.5 support to the load\_schedule\_grid command.

## 0.1.9

* Add a command to load schedule grid from YAML

## 0.1.8

* Add a badger for accepted talks
* Add travel\_from to the bursary export.

## 0.1.7

* List exports in front desk
* Add bursaries export

## 0.1.6

* Further improvements to the bursary notification email.

## 0.1.5

* Add management command to remind users to register.
* Include some details, useful for visas in the registration
  confirmation email.
* Handle unassigned rooms, correctly.
* Clear travel expense amount, when cancelling a travel bursary request.
* Add a CSV export for Child Care.
* Display meal lists, in order.
* Remove DC18 details from the bursary notification email.

## 0.1.4

* Correct the permission checked by bursary admin pages.

## 0.1.3

* Add a Volunteer Admin group.
* Add Kosovo to the list of countries.

## 0.1.2

* SECURITY: Don't show other registered attendees as room-mates, when
  nobody has rooms assigned.

## 0.1.1

* Package now has metadata and license.
* New management commands: `create_debconf_groups`,
  `load_tracks_and_talk_types`.

## 0.1.0

* Initial release, mostly ready for DebConf19.

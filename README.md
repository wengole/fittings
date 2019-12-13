# Fittings
A simple fittings and doctrine management app for [allianceauth](https://gitlab.com/allianceauth/allianceauth).

## Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Updating](#updating)
- [Settings](#settings)
- [Permissions](#permissions)


## Overview
This plugin serves as a replacement for the now defunct fleet-up service integration. It allows you to create and manage ship fits and doctrines all in a 
central location for your members to browse.

## Key Features
Fittings offers the following features:

* Support for inputting fittings using the EFT format. 
  * Support for pulling fits from ESI *Coming Soon*
* Support for saving fits to EVE via ESI.
* All fits can be copied to the clipboard for ***Buy All***.

## Screenshots

### Dashboard/Doctrine List
![dashboard/doctrine list](https://i.imgur.com/Xk4Eosh.png)

### Add Fitting
![add fitting](https://i.imgur.com/loFrtjj.png)

### Fitting List
![fitting list](https://i.imgur.com/f01q6wI.png)

### View Fitting
![view fitting](https://i.imgur.com/JwKKWUF.png)

### Add Doctrine
![add doctrine](https://i.imgur.com/MXkPI3c.png)

### View Doctrine
![view doctrine](https://i.imgur.com/FzVCb6S.png)

## Installation
### 1. Install App
Install the app into your allianceauth virtual environment via PIP.

```bash
$ pip install fittings 
```

### 2. Configure AA settings

Configure your AA settings (`local.py`) as follows:

- Add `'fittings',` to `INSTALLED_APPS`

### 3. Finalize Install
Run migrations and copy static files. 

```bash
$ python manage.py migrate
$ python manage.py collectstatic
```

Restart your supervisor tasks.

### 4. Populate Types
This can be done one of two ways, either from the command line or from the admin page.

#### 4.1 Command Line
Run the following commands from the command line to populate types.

*Make sure you are running with your allianceauth virtual environment activated and your auth directory (the one
containing `manage.py`) is your current directory!*
```bash
$ python manage.py shell
>>> from fittings.tasks import populate_types
>>> populate_types()
>>> exit()
```

You are now all set to add fittings and doctrines!

#### 4.2 Admin Interface
 1. Navigate to `{your auth url}/admin/django_celery_beat/periodictask/` and click the `Add Periodic Task` button at the top
right corner of the page.
 2. Give your task a name, it doesn't matter what it is, so long as you know what it is.
 3. From the `Task (registered)` dropdown select `fittings.tasks.populate_types`
 4. Uncheck the `Enabled` tick box.
 5. In the `Schedule` section, select any option from any of the dropdowns.
 6. Click `Save`
 7. You should now be back on the page listing all the periodic tasks. Find the one you just created, and check the 
 tick box next to it's name.
 8. From the `Action` dropdown at the top of the table, select `Run Selected Tasks` and click the `Go` button.
 9. The page should reload, with a green banner at the top saying `1 task was successfully run`. Now just wait a few minutes
 while the database populates all the types and related info and you can then start creating your fits and doctrines. 

## Updating
To update your existing installation of Fittings first enable your virtual environment.

Then run the following commands from your allianceauth project directory (the one that contains `manage.py`).

```bash
$ pip install -U fittings
$ python manage.py migrate
$ python manage.py collectstatic
```

Lastly, restart your supervisor tasks.

## Settings
This application has no settings that need to be added to your allianceauth settings (`local.py`) file.

## Permissions

Permission | Description
-- | --
`fitting.access_fittings` | This permission gives users access to the plugin.
`doctrine.manage` | User can add/delete ship fits and doctrines.
# beets-rockbox

beets plugin to build the rockbox database on your computer, directly from your
beets library. this is a test to see if

This should be significantly faster than building the database on device,
taking mere seconds instead of minutes. On a Ryzen 9 3950x i get about 650
songs/sec for building the DB and about 3000 songs/sec for indexing.

## Features

* [x] Build the database
* [x] Sort tags alphabetical
* [x] Write the Database to the device
* [ ] A way to manage statistics data collected by rockbox and sync it with the
  beets library
* [ ] Syncing of music to the device, see [beets-alternatives](https://github.com/geigerzaehler/beets-alternatives)
* [ ] Scrobbling

## Configuration

```yaml
plugins:
  - "rockbox"

rockbox: 
  # Directory to where the rockbox database_*.tcd files are written to, 
  # e.g. the .rockbox folder on your devices. 
  # Will error if the directory doesn't exist. 
  db: "/mnt/ipod/.rockbox"

  # Absolute path where music is stored on the rockbox devices. 
  # This is combined with relative library paths to set the filename 
  # references in the db.
  music: "/<HDD0>/Music"

  # If set, overrides the extension of any files with an extension not in 
  # this list with the first format. You would usually want to set this to 
  # the same values as the formats for your beets-alternatives collection. 
  formats: ["opus", "mp3"]

  # Optional query to restrict which files are included in rockbox database 
  # Usually set to the same value as the beets-alternatives collection. 
  query: "ipod#true"

  # String that is used as placeholder for unknown values in the database. 
  # Default: "<Unknown>" 
  unknown: "<Unknown>" 
```

## CLI Usage

Run `beet rock build` to build the database and write it to your specified
location.

## Limitations

Currently, the database is built from the main beets database/library and no
path formats are set, so if you are using path formats to organize your library
in beets-alternatives differently than your main library this probably won't
work for you.

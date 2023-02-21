# Now/Here  

Simple browser-based note-taking.
- tagging
- full-text search
- location aware
- links
- stores diffs
- uses Flask / Mongo / nginx
- integration with email and Notes.app
- daily backups

Test/develop with `./main.py`  

Deploy with `./launch.sh`

Backup, fetch email, and transfer from Notes with `crontab`



### database

    brew install mongodb-community

    /usr/local/etc/mongod.conf  

    brew services restart mongodb/brew/mongodb-community

### keys

    https://letsencrypt.org/docs/certificates-for-localhost/

let keychain know to always trust

### ref

    https://gist.github.com/mplewis/6076082

### todos

- search phrases
- search dates
- explicit edit button
- "now" link


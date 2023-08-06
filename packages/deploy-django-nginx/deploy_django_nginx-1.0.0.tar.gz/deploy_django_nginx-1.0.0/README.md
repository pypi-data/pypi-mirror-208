# Deploy Django with uWSGI and Frontend with Nginx
- Nginx + uWSGI + Django


### Installation
```bash
python3 -m pip install deploy_django_nginx
```

### Options
```
  -f, --front-end TEXT  the dist directory of frontend  [required]
  -b, --back-end TEXT   the directory of backend  [required]
  -n, --name TEXT       the name of django project  [required]
  -d, --directory TEXT  the directory to deploy  [default: ./deploy]
  -p, --port INTEGER    the port number  [default: 1080]
  -y, --force           force overwrite directory
  -?, -h, --help        Show this message and exit.
```

### Examples
```bash
deploy_django_nginx \
  -b /path/to/api  \                  # backend root directory
  -f /path/to/app/dist/ \             # frontend dist directory
  -n proj \                           # django project name
  -p 1080 \                           # network port
  -d /data2/work/novodb/beet \        # destination directory
```

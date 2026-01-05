# Automatic Railway Deployment

## What Happens Now

Every time you push to GitHub, Railway will automatically:

1. ✅ **Detect the push** to the `main` branch
2. ✅ **Pull the latest code** from GitHub
3. ✅ **Run migrations** automatically (`python manage.py migrate`)
4. ✅ **Start the server** with the new code

## Files Added

### `start.sh`
Startup script that Railway runs on every deployment:
- Runs database migrations first
- Then starts the gunicorn server

### `railway.json`
Railway configuration file that tells it to use `start.sh`

### `Procfile`
Fallback configuration file

## How to Deploy

Simply:
```bash
git add .
git commit -m "your changes"
git push
```

Railway will automatically:
- Deploy your changes
- Run any new migrations
- Restart the server

## Current Status

✅ **Pushed to GitHub** - Railway should now be deploying automatically!

Watch your Railway dashboard to see the deployment progress. You should see:
1. Build starting
2. "Running database migrations..." in the logs
3. "Applying org.0005_simplify_roles... OK"
4. "Starting application..."
5. Deployment complete!

## Next Deployment

From now on, every `git push` will automatically:
- Apply any new migrations
- Deploy the latest code
- No manual steps needed!

---

**Note:** The first deployment with this change will apply the pending migration `0005_simplify_roles` which updates the role structure.

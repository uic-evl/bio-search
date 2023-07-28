# Auth

The authorization module is a NodeJS server that exposes routes to support user
authentication using Passport and JSON web tokens. Currently used by the GXD
Search Interface because of data confidentiality.

## Environmental Variables

For testing/deployment, use a .env file with the following variables or set them
as environmental variables.

- SECRET: Passcode used to hash the values
- CURRYSAUCE: Hardcoded username
- MAYO: Hardcoded user password
- PORT: web server port
- HTTPS: true or false
- PK: private key's path if using HTTPS
- CRT: certificate's path is using HTTPS
- EXPPATH: path for saving logs

## Setting up a new environment

Because this version uses a hardcoded user for authenticating the demo search
page, we need to set in the environmental variables the values to validate
requests for log in. Those values are stored in CURRYSAUCE (username) and MAYO.

To deploy in a new environment:

1. Set the env variables SECRET, PORT, HTTPS, PK and CRT, EXPPATH with valid values.
2. Add to CURRYSAUCE the generic username
3. Add to MAYO a random value because we validate against empty values so the inital value can't be empty.
4. Send a request to /api/users/register with the username=CURRYSAUCE and a
   desired password in the password field
5. Grab the token returned by the request and update MAYO with it
6. Restart the server. Now login and me will validate against the generic user

If you are moving a working environment to another deployment, you need to keep
the SECRET value consistent because the password hashing depends on it.


## Routes

_Register User_

```javascript
/api/users/register POST
// body
{
  "username": "SOME_USERNAME",
  "password": "SOME_PASSWORD"
}
// results
{ "username" } or { "message" } in case of error
```

_Log in user_ generates a valid token for 7 days

```javascript
/api/users/login POST
// body
{
  "username": "SOME_USERNAME",
  "password": "SOME_PASSWORD"
}
// results
{
  "username": "SOME_USERNAME",
  "token": "GENERATED_TOKEN"
}
```

_Validate user_ validates a json web token (as generated in login) against the
server. For the local user version, it reads the username and password from the
environmental variables **CURRYSAUCE** and **MAYO**.

```javascript
/api/users/me GET
// body
{
  "username": "SOME_USERNAME",
}
// authorization type: bearer token with the value of the GENERATED_TOKEN from the login
Add to the Auth header the json web token generated from login
```

## Run

Development

```bash
npm run start // development mode with nodemon
npm run prod  // production mode
```

## Changelog

- 0.0.2: Update jsonwebtoken to 9.0.0 and passport.jwt for security reasons

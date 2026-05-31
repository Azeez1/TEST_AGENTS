# Feature Spec: Google OAuth Authentication

| Field | Value |
|-------|-------|
| **Author** | EZ |
| **Date** | 2026-03-22 |
| **Team** | ENGINEERING_TEAM |
| **Status** | Approved |
| **Priority** | P1 High |

## Problem Statement

Users currently sign up with email/password only. We lose 30-40% of potential signups at the registration form because users don't want to create another password. Adding Google OAuth reduces friction and increases conversion by letting users sign in with one click using their existing Google account.

## Requirements

### Functional Requirements

1. Users can click "Sign in with Google" on the login page and authenticate via Google OAuth 2.0
2. New users who sign in with Google are automatically registered with their Google profile data (name, email, avatar)
3. Existing users who sign in with Google using a matching email address are linked to their existing account
4. Users who signed up with email/password can later link their Google account from settings
5. Users can unlink their Google account if they have an alternative login method (password or another OAuth provider)
6. The Google avatar is used as the default profile picture but can be overridden

### Non-Functional Requirements

1. OAuth flow completes within 3 seconds (excluding Google's consent screen)
2. Tokens are stored securely — refresh tokens encrypted at rest, access tokens never persisted
3. OAuth flow works on mobile browsers (responsive consent redirect)

## Edge Cases

| # | Scenario | Expected Behavior |
|---|----------|-------------------|
| 1 | User's Google email matches existing account with password auth | Prompt user: "An account with this email exists. Link your Google account?" If yes, link. If no, cancel. |
| 2 | User revokes app access in Google account settings | Next login attempt triggers re-consent. Existing account remains valid with password fallback. |
| 3 | Google returns no email (privacy settings) | Show error: "We need your email address to continue. Please allow email access in Google's consent screen." |
| 4 | User has two Google accounts and tries to link both | Allow multiple Google accounts linked to one app account. Each Google ID maps to one app account only. |
| 5 | Google OAuth service is temporarily down | Show friendly error: "Google sign-in is temporarily unavailable. Please use email/password or try again later." |
| 6 | User tries to unlink Google when it's their only auth method | Block with message: "Set a password first before unlinking Google." |

## Acceptance Criteria

```gherkin
Given a new user
When they click "Sign in with Google" and authorize the app
Then they are redirected to the onboarding flow with their name, email, and avatar pre-filled from Google

Given an existing user with email/password auth
When they click "Sign in with Google" using the same email
Then they are prompted to link accounts, and upon confirmation, both auth methods work

Given a user signed in with Google
When they navigate to Settings > Linked Accounts
Then they see Google listed with their Google email and an "Unlink" button

Given a user with only Google auth (no password set)
When they click "Unlink" on their Google account
Then the unlink is blocked with a message to set a password first

Given Google's OAuth service is down
When a user clicks "Sign in with Google"
Then they see a friendly error message and can fall back to email/password login

Given a user who previously authorized the app
When they click "Sign in with Google" again
Then they are signed in immediately without re-consent (using stored refresh token)
```

## Out of Scope

- Other OAuth providers (GitHub, Apple) — separate spec
- Two-factor authentication — existing feature, no changes needed
- Admin ability to disable Google OAuth — future enhancement
- Migration of existing users to Google auth — users self-serve via settings

## Dependencies

- Google Cloud Console project with OAuth 2.0 credentials configured
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` environment variables
- Existing user model must support multiple auth providers (verify schema)
- Email service for "account linked" notification

## Notes

- Google's OAuth 2.0 docs: https://developers.google.com/identity/protocols/oauth2
- Consent screen must be configured in Google Cloud Console before testing
- For development, use `http://localhost:3000/auth/callback/google` as redirect URI

# remove_apple_autosave

Apple's Mail.app stores autosave messages in the Gmail archive that can become a huge annoyance.

Fortunately, all of these mail messages are identified with the `X-Apple-Auto-Saved` header.

This program authenticates to Gmail server using OAuth2 and then
deletes the autosave files. You can run it as often as you wish.

The program uses Gmail's API with batching. However, because of the
interaction between Mail.app's frequent saves and Gmail rate limits,
the cleanup can take a long time.

## Installation

git clone https://github.com/simsong/remove_apple_autosave
cd remove_apple_autosave
make install
make run

# Background URLs:
https://developers.google.com/gmail/api/guides/batch

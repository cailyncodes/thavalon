# Thavalon
Thavalon is a expanded variant of Avalon which prioritizes everyone getting a special role. You can read more about it at [thavalon]().

This web app implements the game with support for role distribution, mission voting, and other functionality to speed up in person games.

We also have developed some of our own rules and new roles, which you can read about below.

## Custom Rules
We have played over a hundred games and scores of hours over the past several years. Through this, we have developed some custom rules which we think greatly improve the experience and balance of the game.

1. In 5, 6, and 7 player games, Modred must be in play.
2. In 6 player games, we always play our "Jealousy" variant.

### Additional Roles
1. Jealous Ex. Evil. They see either Tristan or the Older Sibling without knowing the role thereof.
2. Older Sibling. Good. They are seen by the Jealous Ex and sees one good player without knowing the role thereof.

# Development
This app is implemented as a Next JS client and Python API in a monorepo.

For local development, we use [Podman](https://podman.io/) for managing containers.

### Installation

1. Clone the repo.
1. Install Podman CLI. On Mac, use [this link](https://github.com/containers/podman/releases/download/v4.9.2/podman-installer-macos-amd64.pkg). Note: We use Podman v4.9 since v5.0 requires EFI, which is unavailable on older Mac OS versions.
1. Run `podman machine init`
1. Run `podman machine start`

We support VSCode as the editor of choice. The easiest approach is to open `thavalon.code-workspace`.

### Running
We have developed wrapper scripts to help support development.

You can start both services with our `./run.sh` script.

`./run.sh start`

The first time you run this, it will take several minutes, as the `node_modules` directory needs to be populated and copied onto the host via the bind mount.

Services can be stopped likewise.

`./run.sh stop`

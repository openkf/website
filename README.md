# OpenKF's docs

This repository uses [Hugo](https://gohugo.io/) and the Docsy v0.9.1 module.
The theme is pinned in `go.mod` and `go.sum`.

## Requirements

- Node.js 22 LTS, using the version in `.nvmrc`.
- Hugo extended 0.121.2, matching the Netlify configuration.
- Go 1.21.5 or later, for Hugo Modules. CI uses Go 1.26.10.

Install Hugo extended using the
[official installation instructions][hugo-install].
The npm install step does not download a separate Hugo executable.

[hugo-install]: https://gohugo.io/installation/

## Install dependencies

```bash
npm ci
```

The committed lock file records the dependency tree. Keep it when cleaning
local build output or reinstalling dependencies.

## Preview locally

```bash
npm run start
```

Use `npm run create -- path/to/page.md` to add a real documentation page.
This checkout currently has no `content` directory.

## Build

```bash
npm run build
```

This runs Hugo in production mode, including Docsy's PostCSS stylesheet
pipeline, and writes the result to `public`.

To include draft and future pages in a preview build:

```bash
npm run build:preview
```

## Check Markdown

```bash
npm test
```

The Markdown rules cover root Markdown files and any pages under `content`.
To apply the linter's supported fixes:

```bash
npm run lint:markdown-fix
```

The linter uses narrowly scoped RE2JS and KaTeX security patch overrides below
`markdownlint` 0.42.0 until its publisher updates those dependency pins.

## CI

CI installs the locked dependencies, checks Markdown, and builds the actual
repository with Node.js 22 and Hugo extended on Linux, Windows, and macOS.
It also creates a temporary synthetic Docsy page and style to check the real
production HTML, stylesheet link, and PostCSS/autoprefixer output. That context
is removed afterward; synthetic content is never added to the product site.

## Repository layout

- `hugo.toml`, `go.mod`, and `go.sum`: the pinned Docsy module.
- `i18n`: local translation overrides.
- `postcss.config.cjs`: the production autoprefixer plugin.
- `package.json` and `package-lock.json`: build and Markdown tooling.
- `scripts/check-docsy.py`: the temporary CI production build contract.

## Clean build output

```bash
npm run clean
```

This removes `public` and `resources` without deleting the lock file.

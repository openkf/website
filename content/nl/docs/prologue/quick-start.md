---
title: "Quick Start"
description: "One page summary of how to start a new openkf project."
lead: "One page summary of how to start a new openkf project."
date: 2020-11-16T13:59:39+01:00
lastmod: 2020-11-16T13:59:39+01:00
draft: false
images: []
menu:
  docs:
    parent: "prologue"
weight: 110
toc: true
---

## Requirements

openkf uses npm to centralize dependency management, making it [easy to update]({{< relref "how-to-update" >}}) resources, build tooling, plugins, and build scripts:

- Download and install [Node.js](https://nodejs.org/) (it includes npm) for your platform.

## Start a new openkf project

Create a new site, change directories, install dependencies, and start development server.

### Create a new site

openkf is available as a child theme, and a starter theme:

- Use the openkf child theme, if you do __not__ plan to customize a lot, and/or need future openkf updates.
- Use the openkf starter theme, if you plan to customize a lot, and/or do __not__ need future openkf updates.

Not quite sure? Use the openkf child theme.

#### openkf child theme

```bash
git clone https://github.com/openkf/website-child-theme.git my-openkf-site
```

#### openkf starter theme

```bash
git clone https://github.com/openkf/website.git my-openkf-site
```

### Change directories

```bash
cd my-openkf-site
```

### Install dependencies

```bash
npm install
```

### Start development server

```bash
npm run start
```

openkf will start the Hugo development webserver accessible by default at `http://localhost:1313`. Saved changes will live reload in the browser.

## Other commands

openkf comes with commands for common tasks. [Commands →]({{< relref "commands" >}})

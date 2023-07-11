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

- [Git](https://git-scm.com/) — latest source release
- [Node.js](https://nodejs.org/) — latest LTS version or newer

{{< details "Why Node.js?" >}}
openkf uses npm (included with Node.js) to centralize dependency management, making it [easy to update]({{< relref "how-to-update" >}}) resources, build tooling, plugins, and build scripts.
{{< /details >}}

## Start a new openkf project

Create a new site, change directories, install dependencies, and start development server.

### Create a new site

openkf is available as a child theme and a starter theme.

#### Child theme

- Intended for novice to intermediate users
- Intended for minor customizations
- [Easily update npm packages]({{< relref "how-to-update" >}}) — __including__ [openkf](https://www.npmjs.com/package/@hyas/openkf)

```bash
git clone https://github.com/openkf/website-child-theme.git my-openkf-site
```

#### Starter theme

- Intended for intermediate to advanced users
- Intended for major customizations
- [Easily update npm packages]({{< relref "how-to-update" >}})

```bash
git clone https://github.com/openkf/website.git my-openkf-site
```

{{< details "Help me choose" >}}
Not sure which one is for you? Pick the child theme.
{{< /details >}}

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

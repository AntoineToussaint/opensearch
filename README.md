# Welcome to your workspace argon!

## What is a workspace?

A workspace is meant to be represent a monorepo of applications that are related to each other.

See [Documentation](https://docs.codefly.dev/concepts/workspace/) for more information.

## Structure of the workspace

The workspace is structured as follows:
```shell
workspace/
├── 📂 configurations
|   ├── 📂 ${dev}
│   └── 📂 ${production}
└── 📂 services
│   ├── 📂 ${frontend}
│   ├── 📂 ${backend}
│   └── 📂 ${database}
```

`configurations` contains the shared configurations for the workspace.

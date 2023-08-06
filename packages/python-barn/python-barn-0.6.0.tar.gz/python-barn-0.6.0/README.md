# barn

barn is a Python-based command-line interface (CLI) tool that simplifies package management by providing an intuitive set of commands.
It was inspired by the **yarn** counterpart from Javascript.
Hence the interface was kept as similar as possible, so that if you are familiar with yarn you should pickup barn relatively fast.

> **Note**
> Barn is just a pip wrapper, so package resolution is still completely
> up to pip and your installed pip version

## Features

- Install packages
- Add new packages
- Initialize new projects with interactive prompts
- Ability to define script scoped to your project, like you would do with a package.json

### ⚠️ A small invite to caution

Barn is still in development and can be unstable.
More over:

- It currently only supports python 3.9 and it is only officially tested on 3.9.13
- It still lacks core feature that hopefully will be added soon

## How to use

You can install barn directly with the following pip command:

> **Note**
> You are encouraged to install barn globally on your system

```
pip install python-barn
```

#### You can initialise an empty directory to be a barn project by running:

```
barn init
```

This will launch an interactive prompt asking for details such as project name, description, author, etc.

In case your project already exists and it's not an empty folder, you can create the `project.yaml` file with the following content:

```
name: my-project
description: Some description
version: 0.1.0
author: your-name or your team name
scripts:
  - start: python ./main.py
  - test: echo "Not implemented"
license: your-license
```

#### Install project dependencies

```
barn
```

or

```
barn install
```

#### Add a new package:

```
barn add <package-name>
```

#### Remove a package:

```
barn remove <package-name>
```

#### To setup custom scripts

In the project.yaml, you can specify bash scripts by adding to the scripts section:

```
scripts:
  - start: python ./main.py
```

Once you have your script defined you can run:

```
barn <script-name>
```

In this case:

```
barn start
```

This will run your script in the context of the project, with the correct python version and pointing to the correct virtual environment

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

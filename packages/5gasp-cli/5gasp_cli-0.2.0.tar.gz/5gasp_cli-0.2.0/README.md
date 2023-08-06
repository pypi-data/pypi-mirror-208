# 5GASP CLI

## How to run

You can find the code inside the */5gasp-cli/src/* directory.
To list all CLI commands, run:

```
5gasp-cli --help
```

To list all parameters of a command, run:
```
5gasp-cli COMMAND --help
```

### CLI Commands

#### List all tests from a test bed

```
5gasp-cli list-testbeds
```

#### List all available tests

```
5gasp-cli list-available-tests
```

#### Generate a testing descriptor:

```
5gasp-cli create-testing-descriptor
```

This command has the following options:

* One or more NSDs (Network Service Descriptors) can be passed to infer connection point tags from, using the following command:

```
5gasp-cli create-testing-descriptor --infer-tags-from-nsd <nsd_location>
```

* The path of the generated descriptor can be passed using:

```
5gasp-cli create-testing-descriptor --output-filepath <path_to_file>
```

> **_NOTE:_** Both options can be used simultaneously
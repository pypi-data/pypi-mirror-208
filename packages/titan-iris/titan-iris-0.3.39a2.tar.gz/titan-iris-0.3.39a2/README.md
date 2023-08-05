# IRIS CLI Package.

## Description

Iris is your portal to the TitanML platform. Using Iris, you can launch jobs to run on TitanML servers, run your own models and datasets through our compression algorithms, and explore and download the optimised models from the Titan Store.
The backend takes one of the following supported models and uses it to finetune similar, smaller models. The training signals from the teacher model improve the performance of the student model on edge cases, and allow you to use cheaper, more readily-available unlabelled data.

## Getting Started

### Dependencies

* python >= 3.7
* titanML login

### Installing

* using pip

```
pip install titan-iris
```

___

# iris API

## <mark style="color:purple;">`iris`</mark>

**Usage**:

<pre class="language-console"><code class="lang-console"><strong>$ iris [OPTIONS] COMMAND [ARGS]...
</strong></code></pre>

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `delete`: delete objects from the TYTN api.
* `download`: Download the titan-optimized onnx model.
* `get`: Get objects from the TYTN api.
* `infer`: Run inference on a model.
* `login`: Login to iris.
* `logout`: Logout from iris.
* `makesafe`: Convert a non-safetensor model into a...
* `post`: Dispatch a job to the TitanML platform
* `pull`: Pull the titan-optimized server docker image.
* `status`: Get the status of an experiment
* `upload`: Upload an artefact to the TitanML hub.





### <mark style="color:purple;">`iris delete`</mark>

delete objects from the TYTN api.

**Usage**:

```console
$ iris delete [OPTIONS] [OBJECT]:[experiment|artefact]
```

**Arguments**:

* `[OBJECT]:[experiment|artefact]`: What type of object to delete \[default: experiment]

**Options**:

* `-i, --id TEXT`: Which object to delete \[required]
* `--help`: Show this message and exit.

### <mark style="color:purple;">`iris download`</mark>

Download the titan-optimized onnx model.

**Usage**:

```console
$ iris download [OPTIONS] IMAGE
```

**Arguments**:

* `IMAGE`: The model to pull. Should be displayed in the TitanML Hub. \[required]

### <mark style="color:purple;">`iris get`</mark>

Get objects from the TYTN api.

**Usage**:

```console
$ iris get [OPTIONS] [OBJECT]:[experiment|artefact]
```

**Arguments**:

* `[OBJECT]:[experiment|artefact]`: What type of object to get \[default: experiment]

**Options**:

* `-i, --id TEXT`: Which object to get. None, or '' correspond to getting all objects. Evaluated server-side.
* `-q, --query TEXT`: A JMESPath string, to filter the objects returned by the API. Evaluated client-side.
* `-h, --headers TEXT`: Headers to send with the get request. Should be provided as colon separated key value pairs: -h a:b -h c:d -> {a:b, c:d} \[default: ]
* `--help`: Show this message and exit.

### <mark style="color:purple;">`iris infer`</mark>

Run inference on a model.

**Usage**:

```console
$ iris infer [OPTIONS]
```

**Options**:

* `--target TEXT`: The url to run the server on. \[default: localhost]
* `-p, --port INTEGER`: The port to run the server on. \[default: 8000]
* `-t, --task [sequence_classification|glue|question_answering|token_classification]`: The task to optimize the model for. \[required]
* `--use-cpu`: Whether to use the CPU. If False, the GPU will be used. Choose CPU only when the opmitized model is in CPU format(OnnxRuntime). The default will be False. (using TensorRT) \[default: False]
* `-t, --text TEXT`: The text to run the server in. In classification tasks, this is the TEXT to be classified. In question answering tasks, this is the QUESTION to be answered. \[required]
* `-c, --context TEXT`: The context in question answering tasks. Only used in question answering tasks. \[default: ]
* `--help`: Show this message and exit.

### <mark style="color:purple;">`iris login`</mark>

Login to iris.

**Usage**:

```console
$ iris login [OPTIONS]
```

### <mark style="color:purple;">`iris logout`</mark>

Logout from iris.

**Usage**:

```console
$ iris logout [OPTIONS]
```

### <mark style="color:purple;">`iris makesafe`</mark>

Convert a non-safetensor model into a safetensor model, including for models with shared weights.

**Usage**:

```console
$ iris makesafe [OPTIONS] [MODEL]
```

**Arguments**:

* `[MODEL]`: The model to convert to safe\_tensors \[default: model]

### <mark style="color:purple;">`iris post`</mark>

Dispatch a job to the TitanML platform.

**Usage**:

```console
$ iris post [OPTIONS]
```

**Options**:

* `-m, --model TEXT`: The model to optimize. \[required]
* `-d, --dataset TEXT`: The dataset to optimize the model with. \[required]
* `-t, --task [sequence_classification|glue|question_answering|token_classification]`: The task to optimize the model for. \[required]
* `-n, --name TEXT`: The name to use for this job. Visible in the TitanML Hub. \[default: ]
* `-f, --file TEXT`: Load the options from a config file \[default: ]
* `-s, --short-run`: Truncates the run after 1 batch and 1 epoch. Will provide bad results, but useful to check that the model and dataset choices are valid. \[default: False]
* `-nl, --num-labels INTEGER`: Number of labels. Required for task sequence\_classification
* `-tf, --text-fields TEXT`: Text fields. Required for task sequence\_classification
* `-hn, --has-negative`: Has negative. Required for question\_answering \[default: False]
* `-ln, --label-names TEXT`: Names of token labels. Required for task token\_classification. Specify as a mapping with no spaces: `-ln 0:label1 -ln 1:label2`
* `--help`: Show this message and exit.

### <mark style="color:purple;">`iris pull`</mark>

Pull the titan-optimized server docker image.

**Usage**:

```console
$ iris pull [OPTIONS] IMAGE
```

**Arguments**:

* `IMAGE`: The image to pull. Should be displayed in the TitanML Hub. \[required]

### <mark style="color:purple;">`iris status`</mark>

Get the status of an experiment

**Usage**:

```console
$ iris status [OPTIONS]
```

**Options**:

* `-i, --id INTEGER`: The id of the experiment to get the status of \[required]

### <mark style="color:purple;">`iris upload`</mark>

Upload an artefact to the TitanML Hub.

**Usage**:

```console
$ iris upload [OPTIONS] SRC [NAME] [DESCRIPTION]
```

**Arguments**:

* `SRC`: The location of the artefact on disk. Should be a folder, containing either a model or a dataset. For more information on the supported formats, see [here](../launching-a-job/using-iris-upload.md). \[required]
* `[NAME]`: The name of the artefact. Displayed in the TitanMl Hub.
* `[DESCRIPTION]`: A short description of the artefact. Displayed in the TitanML Hub.

**Options**:

* `--help`: Show this message and exit.


## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

TitanML


## Version History

## License

## Acknowledgments

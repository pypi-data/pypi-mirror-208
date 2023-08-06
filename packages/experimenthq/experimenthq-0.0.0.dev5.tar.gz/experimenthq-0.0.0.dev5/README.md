


<div align="center">



<img src="https://www.experiment-hq.com/_next/image?url=%2Flogo.png&w=3840&q=75"  width="15%" class="center" >

# ExperimentHQ

</div>


ExperimentHQ is a Python package that allows you to track and manage experiments directly from your Python code, and seamlessly sync the results to a Notion database. With ExperimentHQ, you can easily monitor the performance of your models, log custom metrics, and compare experiments with ease, all from a single, intuitive interface.

The purpose of this document is to provide a guide for using ExperimentHQ to track experiments and sync the results to Notion.

## Prerequisites

Before you can use ExperimentHQ, you need to set up the following prerequisites:

1. Set up a Notion account.
2. Set up an [ExperimentHQ](http://www.experiment-hq.com/) account.
3. Connect you Notion account with [ExperimentHQ](http://www.experiment-hq.com/account) 
4. Copy your personal API token from [ExperimentHQ](http://www.experiment-hq.com/account)
5. Install ExperimentHQ.

## Installation

To install ExperimentHQ, simply run the following command:

```bash
pip install experimenthq
```

## Usage

### Creating an Experiment
To create an experiment and log it to Notion, you can use the following code snippet as an example:

```python
import experimenthq as ex

experiment = ex.Experiment(
    name="My First Experiment",
    project="Project A",
    api_key="YOUR_API_KEY"
)

experiment.log_parameter("accuracy", 0.85)
experiment.log_parameter("loss", 0.05)

```

This code creates an experiment with the name "My First Experiment" and tags it with the project "Project A". It then logs two parameters, "accuracy" and "loss", with values 0.85 and 0.05 respectively.

### Viewing Experiments in Notion

To view the experiments that you've logged with ExperimentHQ in Notion go to the Notion page that you've linked to ExperimentHQ. You should see a table with the experiments that you've logged.

![Notion Table](https://www.experiment-hq.com/_next/image?url=%2Fnotion_dashboard.png&w=3840&q=75)

## Conclusion
ExperimentHQ provides a simple and intuitive way to track and manage your experiments in Python and sync the results to Notion. By using ExperimentHQ, you can streamline your experiment tracking and make your work more efficient and effective. Try it out today and see the difference it can make in your workflow!

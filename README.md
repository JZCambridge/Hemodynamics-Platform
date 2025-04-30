# Hemodynamics Platform

The cornerstone of the main author's doctoral work was the introduction of 'mechanomics' into coronary CFD analysis. By integrating this novel concept and coronary computed tomography angiography (CCTA)-derived radiomic and morphological information, this Python-Qt based interface was developed to automate high-throughput feature extraction. This innovation drastically reduced analysis time from two months to a mere four hours per case. 

Picture added later

## Citation

## Getting Started
Jay First Correct 

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

For Python + Conda + Windows environment set up:

Win + R type 'cmd' open terminal
```bash
activate
conda env create -f environment.yml
```

linux + docker
docker build -t hymoplatform .

On Linux hosts, first run:
xhost +local:docker

docker run -it --rm --gpus all -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY -v $HOME/.Xauthority:/root/.Xauthority --device=/dev/dri:/dev/dri --ipc=host -v $(pwd):/app hymohlatform

docker run -it --rm --gpus 1 --shm-size 16G -v /tmp/.X11-unix:/tmp/.X11-unix -v ~/ukb:/ukb -v ~/cardiac:/cardiac -v ~/temp:/temp -v ~/jzheng12:/jzheng12 -e DISPLAY=$DISPLAY -v $HOME/.Xauthority:/root/.Xauthority --device=/dev/dri:/dev/dri --ipc=host -v $(pwd):/app hymohlatform

/ukb/template_wenjia/vtks/LVmyo_ED.vtk

/ukb/jz_ukbb_18k/collection_1/1000213/lvsa_SR_ED.nii.gz
0 350
0 350
40 40

/ukb/jz_ukbb_18k/collection_1/1000213/lvsa_ED.nii.gz

/ukb/jz_ukbb_18k/collection_1/1000213/vtks/F_LVmyo_ED.vtk



### Installing

A step by step series of examples that tell you how to get a development environment running:

Say what the step will be:

\```bash
Give the example
\```

And repeat:

\```bash
until finished
\```

End with an example of getting some data out of the system or using it for a little demo.

## Running the tests

Explain how to run the automated tests for this system.

### Break down into end-to-end tests

Explain what these tests test and why:

\```bash
Give an example
\```

### And coding style tests

Explain what these tests test and why:

\```bash
Give an example
\```

## Deployment

Add additional notes about how to deploy this on a live system.

## Built With

* [PyQt5](https://riverbankcomputing.com/software/pyqt/intro) - The GUI framework used
* [Python](https://www.python.org/) - Programming Language

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Your Name** - *Initial work* - [YourGithubUsername](https://github.com/YourGithubUsername)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc

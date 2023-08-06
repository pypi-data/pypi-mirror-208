<a href="https://www.islas.org.mx/"><img src="https://www.islas.org.mx/img/logo.svg" align="right" width="256" /></a>

# NERD: Numerical Estimation of Rodenticide Density

The eradication of rodents is central to island restoration efforts and the aerial broadcast of
rodenticide bait is the preferred dispersal method.
To improve accuracy and expedite the evaluation of aerial operations, we developed an algorithm for
the numerical estimation of rodenticide density (NERD).
The NERD algorithm performs calculations with increased accuracy, displaying results almost in real-time.
NERD describes the relationship between bait density, the mass flow rate of rodenticide through the
bait bucket, and helicopter speed and produces maps of bait density on the ground.
NERD also facilitates the planning of helicopter flight paths and allows for the instant
identification of areas with low or high bait density.

## Installation

```
pip install geci-nerd
```

## Jupyter Notebook Demonstrations

You can explore the functionality of NERD through interactive Jupyter notebooks.
These are the options to access the demonstration notebooks:

- Visit [IslasGECI.org](http://islasgeci.org:8080) for an online Jupyter Notebook environment.
- View a static version on GitHub.
  Simply navigate to the ["examples"](https://github.com/IslasGECI/nerd/blob/develop/examples/) folder.
- Alternatively, you can run the Jupyter notebooks locally using Docker.
  Follow the instructions below:

First, pull the latest demo image:

```shell
docker pull islasgeci/nerd_demo:latest
```

Then, run the container:

```shell
docker run --detach --publish 8080:8888 --rm islasgeci/nerd_demo
```

Lastly, explore the Jupyter notebooks at http://localhost:8080/

## References

- [Improving the efficiency of aerial rodent eradications by means of the numerical estimation of
  rodenticide density](https://www.islas.org.mx/articulos_files/Rojas-Mayoral%202019.pdf)

---

[Grupo de Ecología y Conservación de Islas](https://www.islas.org.mx/)

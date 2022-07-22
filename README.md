# ant-analysis
analysis code for ant project

## Trajectory output processing

After exporting trajectory from SLEAP (output is a .h5 file), go to `tracking` folder and run:

``` python sleap_trajectory_extraction.py -f [EXPERIMENT ID (without .h5)] -s 1 ```

the -s flag is to decide whether or not to skip the step for re-stitching trajectory to fix erroneous links or fragments, but the python version of that process is incomplete so just use 1 for now. The search directory for input file is `data/trajectories/` and the output is saved in the same directory with `_proc` appended to the original file name. The Mathematica notebook, `sleap_trajectory_extraction.nb` is able to perform the equivalent task including the trajectory restitching.

## Clustering analysis

### Computing distance matrix

To compute and save the distance matrix, go to `cluster_analysis` folder and run

``` python distance_mapping.py -f FILENAME ```

The input file is searched from `data/trajectories/` and the output is saved to `data/clustering/`.

### Plotting radial distribution function

The radial distribution function is plotted based on the distance matrix. This code only adds normalization factor to each bin. Note that because the data is collected using a bounded plane, in principle the normalization factor needs to exclude sectors that lie outside the bounding box. This is complicated so right now it just assumes the plane is infinite, meaning the distribution is slightly (or maybe significantly) off. It is currently hardcoded to save these figures every 250 frames. To use, run

``` python plot_distances.py -f FILENAME -v VIDEONAME ```

The video input is not set to required on purpose but right now it will probably crash the code if it's not supplied. It is included so that the RDF plot can be viewed alongside the frame that produced it.

### Performing K-Means Clustering

To perform K-Means Clustering simply run

``` python kmc.py -f FILENAME -v VIDEONAME ```

For same reason as above the video is set to optional but will crash the code if not supplied. This generates two figures for each frame, one is the elbow plot to show the estimation for optimal k parameter and the other plot is a visualization of the cluster for the frame in concern. It is currently hardcoded to save these figures every 250 frames.
